import os

from . import objects
from . import settings
from . import tileset
from . import globs
from . import animation
from . import sound
from . import data
from . import script_engine
from . import events
import eng.behaviours as behaviours
import eng.movement as movement

from eng.constants.directions import *
from eng.constants.behaviours import *

#define sprite status constants
S_WALK = 0
S_RUN = 1
S_BIKE = 2
S_TERRAIN = 3

class Sprite(objects.VisibleObject):
   """Class for moving, animated sprites."""
   
   def __init__(self, node, mMap, position=None, level=None):
      """
      aa

      node - the <sprite> node.
      mMap - the map to put the sprite on.
      position - the position to start at. If None it gets taken from the node.
      level - the level to start on. If None it gets taken from the node.
      """

      #init the VisibleObject
      objects.VisibleObject.__init__(self)

      #store the map for later
      self.map = mMap

      #create the tileset
      #determine the tile offset, so that the sprite is drawn at the centre bottom of a map tile
      tsId = node.getAttr("tileset", data.D_STRING)
      self.tileset = tileset.Tileset(tsId)

      #determine position, and initialise destination to position
      if position is None:
         self.position = tuple(node.getAttr("position", data.D_INT2LIST))
      else:
         self.position = position
      self.destination = self.position

      #determine the level
      if level is None:
         self.level = node.getAttr("level", data.D_INT)
      else:
         self.level = level

      #direction
      direction = node.getOptionalAttr("direction", data.D_STRING)
      if direction is None:
         self.direction = DIR_DOWN
      else:
         try:
            self.direction = STEPNAMES[direction]
         except KeyError:
            raise error.DevError("No direction called \"{}\".".format(direction))

      #find out the id, if there is one
      self.id = node.getOptionalAttr("id", data.D_STRING, None)

      #initialise variables
      self.status = S_WALK
      self.speed = 1 #walking
      self.walkCycle = 0
      self.busy = False
      self.switch = False
      self.locked = False
      self.sliding = False
      self.forced = False
      self.climbingWaterfall = False
      self.jumpDir = None
      self.jumpHeight = 0
      self.hasBumped = False
      self.stepQueue = []
      self.bubble = None
      self.bubbleTimer = 0

      #no script engine given yet
      self.scriptEngine = script_engine.ScriptEngine()

      #for scripting
      self.scriptCommands["foo"] = self.command_foo
      self.scriptCommands["move"] = self.command_move
      self.scriptCommands["look"] = self.command_look
      self.scriptCommands["exclamation"] = self.command_exclamation

      #create the basic walk animations
      #set the current animation but don't play it (so it can be ticked without errors)
      self.animations[DIR_UP] = animation.Animation([12,12,13,13,14,14,15,15])
      self.animations[DIR_DOWN] = animation.Animation([0,0,1,1,2,2,3,3])
      self.animations[DIR_LEFT] = animation.Animation([4,4,5,5,6,6,7,7])
      self.animations[DIR_RIGHT] = animation.Animation([8,8,9,9,10,10,11,11])
      self.animation = self.animations[0]

   def tick(self):
      """Tick the sprite one frame."""

      #if we're performing a step, advance the walk cycle
      #if this finishes a step, set the new position and reset walk cycle
      #check for if we're on a switch and unreserve our position
      if self.busy:
         self.walkCycle += self.speed
         if self.walkCycle >= 8:
            self.position = self.destination
            self.walkCycle = 0

            #check for a switch move permission
            #action is got by taking the permission mod 8
            col = self.map.getCollisionData(self.position)
            action, level = movement.getActionLevel(col)
            if action == movement.SWITCH:
               self.switch = True
            else:
               #if we just walked off a switch tile, set the level to that of the switch tile
               #level is got as 1 less than the permission divided by 8 rounded down
               if self.switch:
                  self.level = level
               self.switch = False

            #unreserve our position, now we've actually reached it
            if self.position in self.map.reservedPositions:
               self.map.reservedPositions.pop(self.position)

            #no longer busy
            if self.stepQueue:
               nextDir = self.stepQueue.pop(0)
               self.walk(nextDir, True)
            else:
               self.busy = False
               if self.sliding:
                  b = self.map.getBehaviourData(self.position)
                  self.map.processBehaviour(b, events.EV_FINISHWALKONTO, self)
               self.forced = False

      if self.jumpDir == DIR_UP:
         self.jumpHeight += 1
         if self.jumpHeight >= 8:
            self.jumpDir = DIR_DOWN
      elif self.jumpDir == DIR_DOWN:
         self.jumpHeight -= 1
         if self.jumpHeight <= 0:
            self.jumpDir = None

      if self.bubbleTimer > 0:
         self.bubbleTimer -= 1
         if self.bubbleTimer <= 0:
            self.bubble = None

      #tick the Visible Object (deals with animations)      
      objects.VisibleObject.tick(self)

   def getTile(self):
      """Get the current tile of the sprite."""

      #if we're animated, used the animation to get the tile index
      #else just return the correct standard tile
      if self.sliding or self.jumpDir in (DIR_UP, DIR_DOWN) or self.forced:
         if self.direction == DIR_UP:
            i = 13
         elif self.direction == DIR_DOWN:
            i = 1
         elif self.direction == DIR_LEFT:
            i = 5
         elif self.direction == DIR_RIGHT:
            i = 9
      else:
         if self.animation.active:
            i = self.animation.currentFrame
         elif self.direction == DIR_UP:
            i = 12
         elif self.direction == DIR_DOWN:
            i = 0
         elif self.direction == DIR_LEFT:
            i = 4
         elif self.direction == DIR_RIGHT:
            i = 8

      #return the actual tile
      return self.tileset[i]

   def getMoveOffset(self):
      """Find the offset of the sprite due to movement."""

      #steps take 8 frames to complete, so divide the tile into 8 and use walk cycle to determine position
      if self.direction == DIR_UP:
         return 0, (-1*self.walkCycle*globs.TILESIZE[1])/8
      elif self.direction == DIR_DOWN:
         return 0, (self.walkCycle*globs.TILESIZE[1])/8
      elif self.direction == DIR_LEFT:
         return (-1*self.walkCycle*globs.TILESIZE[0])/8, 0
      elif self.direction == DIR_RIGHT:
         return (self.walkCycle*globs.TILESIZE[0])/8, 0

   def getJumpOffset(self):
      return (0, -1*self.jumpHeight)

   def getOffset(self):
      """Get the combined offset from tile size and movement."""

      #combine the two offsets and return
      moveOffset = self.getMoveOffset()
      jumpOffset = self.getJumpOffset()
      return self.tileset.tileOffset[0]+moveOffset[0]+jumpOffset[0], self.tileset.tileOffset[1]+moveOffset[1]+jumpOffset[1]

   def getPositionInFront(self, distance=1):
      if self.direction == DIR_UP:
         return self.position[0], self.position[1]-distance
      elif self.direction == DIR_DOWN:
         return self.position[0], self.position[1]+distance
      elif self.direction == DIR_LEFT:
         return self.position[0]-distance, self.position[1]
      elif self.direction == DIR_RIGHT:
         return self.position[0]+distance, self.position[1]

   def canMoveTo(self, col):
      """
      Determine whether the sprite can move to a specific movement permission.

      col - the movement permission.
      """

      #determine level and action
      level = int(col//8)-1
      action = col%8

      #if it's a switch, then if it's on our level, or universal (most likely), we can move to it
      #otherwise not
      if action == movement.SWITCH:
         if level == self.level or level == -1:
            return True
         else:
            return False

      #if it's a block, we can't move to it   
      elif action == movement.BLOCK:
         return False

      #if it's clear, then if it's on our level or universal, or we're currently on a switch, we can move to it
      #otherwise not
      elif action == movement.CLEAR:
         if level == self.level or level == -1 or self.switch:
            return True
         else:
            return False

      #if it's a bridge, we can move to it on any level
      #MAYBE CHANGE - so it requires that you must be on the block's level or higher??
      elif action == movement.BRIDGE:
         return True

      #for Surf-style HMs
      elif action == movement.TERRAIN:
         if self.status == S_TERRAIN:
            return True
         else:
            return False

      #ledges
      elif action == movement.LEDGE:
         b = self.map.getBehaviourData(self.getPositionInFront())
         ledgeDir = behaviours.BUILTINBEHAVIOURS[b]
         
         if ledgeDir == B_LEDGEDOWN:
            if self.direction == DIR_DOWN:
               return True
         elif ledgeDir == B_LEDGELEFT:
            if self.direction == DIR_LEFT:
               return True
         elif ledgeDir == B_LEDGERIGHT:
            if self.direction == DIR_RIGHT:
               return True
         
         return False

      #else it's undefined as yet, so we can't go there
      #maybe raise an error instead??
      else:
         return False

   def walk(self, direction, force=False, isPlayer=False):
      """
      Walk (or run etc.) to a new position.

      direction - the direction to move.
      force - if True, bypass checks for being locked or busy.
      isPlayer - True when called by the player.
      """

      #check whether we are able to move
      if (not (self.busy or self.locked) or force) and self.visible:

         #set our direction as given, and calculate the destination position
         self.direction = direction
         if direction == DIR_UP:
            self.destination = self.position[0], self.position[1]-1
         elif direction == DIR_DOWN:
            self.destination = self.position[0], self.position[1]+1
         elif direction == DIR_LEFT:
            self.destination = self.position[0]-1, self.position[1]
         elif direction == DIR_RIGHT:
            self.destination = self.position[0]+1, self.position[1]

         #if we can move to the movement permission, and the map is empty, then start the step
         #set ourselves as busy to start moving when next ticked, and play the correct animation
         #notify the map that we are coming to the destination position
         col = self.map.getCollisionData(self.destination)
         if (self.canMoveTo(col) and self.map.emptyAt(self.destination)) or force:
            self.busy = True
            self.animation = self.animations[direction]
            self.animation.play(False)
            self.hasBumped = False
            if self.status == S_TERRAIN:
               action = movement.getAction(col)
               if not action in (movement.TERRAIN, movement.BRIDGE):
                  self.setStatus(S_WALK)
               if self.climbingWaterfall:
                  b = self.map.getBehaviourData(self.destination)
                  try:
                     builtin = behaviours.BUILTINBEHAVIOURS[b]
                     if builtin != B_WATERFALL:
                        self.climbingWaterfall = False
                  except KeyError:
                     self.climbingWaterfall = False
            self.map.walkonto(self, self.destination, isPlayer)

         #if we can't move to the destination, then if we're the player and we haven't bumped yet, play the sound effect
         else:
            obj = self.map.getPushableAt(self.destination)
            if (obj is not None) and self.map.strengthActive:
               if direction == DIR_UP:
                  objDestination = self.destination[0], self.destination[1]-1
               elif direction == DIR_DOWN:
                  objDestination = self.destination[0], self.destination[1]+1
               elif direction == DIR_LEFT:
                  objDestination = self.destination[0]-1, self.destination[1]
               elif direction == DIR_RIGHT:
                  objDestination = self.destination[0]+1, self.destination[1]
                  
               col = self.map.getCollisionData(objDestination)
               if self.canMoveTo(col) and self.map.emptyAt(objDestination, False):
                  obj.move(direction)
               if isPlayer and not self.hasBumped:
                  sound.playEffect(sound.SD_BUMP)
                  self.hasBumped = True
            else:  
               if isPlayer and not self.hasBumped:
                  sound.playEffect(sound.SD_BUMP)
                  self.hasBumped = True
            self.sliding = False

   def walkForward(self, force=False, isPlayer=False):
      self.walk(self.direction, force, isPlayer)

   def face(self, direction):
      if (not (self.busy or self.locked)) and self.visible:
         self.direction = direction

   def jump(self):
      self.jumpDir = DIR_UP
      self.jumpHeight = 0
      sound.playEffect(sound.SD_JUMP)

   def slide(self):
      self.sliding = True
      self.speed = 2

   def ledge(self):
      self.stepQueue.append(self.direction)
      self.jump()

   def forceTile(self, direction):
      self.forced = True
      self.stepQueue.append(direction)

   def setStatus(self, status):
      self.status = status
      self.tileset = self.statusTilesets[status]

   def setBubble(self, fn, time):
      im = data.getImage(fn, "x")
      im.set_colorkey((255,0,255))
      self.bubble = im
      self.bubbleTimer = time

   def getVar(self, name):
      if name == "level":
         return self.level
      elif name == "visible":
         return self.visible
      elif name == "direction":
         if self.direction == DIR_UP:
            return "UP"
         elif self.direction == DIR_DOWN:
            return "DOWN"
         elif self.direction == DIR_LEFT:
            return "LEFT"
         elif self.direction == DIR_RIGHT:
            return "RIGHT"
      else:
         raise script_engine.DLookupError(name)

   def setVar(self, name, val):
      if name == "level":
         self.level = val
      elif name == "visible":
         self.visible = bool(val)
      else:
         raise script_engine.DLookupError(name)

   def command_foo(self, arg=None):
      if arg:
         print("Called sprite foo with arg: %s" % arg)
      else:
         print("Called sprite foo with no arg")
      return "RETURN"

   def command_move(self, stepString):
      try:
         steps = [STEPNAMES[n.strip()] for n in stepString.split(",")]
      except KeyError as e:
         raise script_engine.DInvalidArgError("walk", stepString, "unrecognised step instruction: %s" % str(e))
      self.walk(steps[0], True)
      if len(steps) > 1:
         self.stepQueue += steps[1:]

   def command_look(self, directionString):
      try:
         direction = STEPNAMES[directionString]
      except KeyError as e:
         raise script_engine.DInvalidArgError("walk", stepString, "unrecognised look direction: %s" % str(e))
      self.direction = direction

   def command_exclamation(self):
      print("!")
      fn = os.path.join(settings.path, "data", "graphics/exclamation.bmp")
      self.setBubble(fn, 20)
               
   def lock(self):
      """Lock the sprite."""
      
      self.locked = True

   def unlock(self):
      """Unlock the sprite."""
      
      self.locked = False
