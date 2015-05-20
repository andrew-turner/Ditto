import random
import math

import pygame

from . import globs
from . import settings
from . import script_engine
from . import plugins

from eng.constants.directions import *
from eng.constants.weather import *

class Overlay():
   def __init__(self, screen):
      self.screen = screen
      
      self.prepareSurface()

   def prepareSurface(self):
      self.surface = self.screen.copy()
      self.surface.fill((100,200,255))

   def flash(self):
      pass

   def draw(self):
      self.screen.blit(self.surface, (0,0))

   def tick(self):
      pass

class DarknessOverlay(Overlay):
   def __init__(self, screen):
      Overlay.__init__(self, screen)

      size = (settings.screenSize[0]*globs.TILESIZE[0],
              settings.screenSize[1]*globs.TILESIZE[1])
      self.maxRadius = int(0.5*math.sqrt((size[0]**2)+(size[1]**2)))

      self.expanding = False
      self.hasExpanded = False
   
   def prepareSurface(self):
      self.surface = self.screen.copy()
      self.surface.set_colorkey((111,0,0))
      
      self.surface.fill((0,0,0))

      self.centre = (int((self.surface.get_width()+1)//2),
                     int((self.surface.get_height()+1)//2))
      self.radius = int(globs.TILESIZE[0]*1.5)
      
      pygame.draw.circle(self.surface, (111,0,0), self.centre, self.radius)

   def flash(self):
      if not self.hasExpanded:
         self.expanding = True

   def draw(self):
      if not self.hasExpanded:
         self.screen.blit(self.surface, (0,0))

   def tick(self):
      if self.expanding:
         self.radius += 2
         pygame.draw.circle(self.surface, (111,0,0), self.centre, self.radius)
         
         if self.radius >= self.maxRadius:
            self.expanding = False
            self.hasExpanded = True

class RainOverlay(Overlay):
   class Raindrop():
      def __init__(self, surface):
         self.surface = surface
         
         self.x = random.randrange(self.surface.get_width())
         self.y = 0

         self.busy = True

      def tick(self):
         self.y += 4
         self.x += 1
         if self.y >= self.surface.get_height():
            self.busy = False

      def draw(self):
         pygame.draw.line(self.surface, (100,140,200), (self.x, self.y), (self.x+3, self.y+5), 2)

   def __init__(self, screen):
      Overlay.__init__(self, screen)

      self.raindrops = []
   
   def prepareSurface(self):
      self.surface = self.screen.copy()
      self.surface.set_colorkey((111,0,0))
      
      self.surface.fill((111,0,0))

   def tick(self):
      for drop in self.raindrops:
         drop.tick()
         if not drop.busy:
            self.raindrops.remove(drop)

      self.raindrops.append(self.Raindrop(self.surface))

      self.surface.fill((111,0,0))
      for drop in self.raindrops:
         drop.draw()

class SandOverlay(Overlay):
   class Sanddrop():
      def __init__(self, surface):
         self.surface = surface
         
         self.x = random.randrange(self.surface.get_width())
         self.y = random.randrange(self.surface.get_height())

         self.gust = random.randint(0,1)
         self.colour = (random.randint(155, 185),
                        random.randint(105, 135),
                        random.randint(0, 20))

         self.busy = True

      def tick(self):
         self.y += self.gust
         self.x -= 3
         if self.y >= self.surface.get_height() or self.x <= 0:
            self.busy = False

      def draw(self):
         #pygame.draw.circle(self.surface, self.colour, (self.x, self.y), 1)
         self.surface.set_at((self.x, self.y), self.colour)
         self.surface.set_at((self.x+1, self.y), self.colour)

   def __init__(self, screen):
      Overlay.__init__(self, screen)

      self.sanddrops = []
   
   def prepareSurface(self):
      self.surface = self.screen.copy()
      self.surface.set_colorkey((111,0,0))
      
      self.surface.fill((111,0,0))

   def tick(self):        
      for drop in self.sanddrops:
         drop.tick()
         if not drop.busy:
            self.sanddrops.remove(drop)

      for i in range(0, 12):
         self.sanddrops.append(self.Sanddrop(self.surface))

      self.surface.fill((111,0,0))
      for drop in self.sanddrops:
         drop.draw()

class Camera(script_engine.ScriptableObject):
   """Class to draw the world onto the screen"""

   #def __new__(cls, *args):
   #   newCls = plugins.checkOverrides(cls)
   #   return script_engine.ScriptableObject.__new__(newCls, *args)
   
   def __init__(self, screen):
      """
      Store the screen and determine the centre tile.
      """

      #store the screen to draw onto later
      self.screen = screen

      #no overlay yet
      self.weather = W_NONE
      self.overlay = None

      #find the tile dimensions of the screen, and identify the centre tile
      self.size = settings.screenSize
      self.centre = (int(((self.size[0]+1)//2)-1),
                     int(((self.size[1]+1)//2)-1))

      #setup scripting
      script_engine.ScriptableObject.__init__(self)
      self.dummy = None
      self.scriptCommands["startDynamic"] = self.command_startDynamic
      self.scriptCommands["endDynamic"] = self.command_endDynamic
      self.scriptCommands["move"] = self.command_move
      self.scriptCommands["flash"] = self.command_flash

      #we're not busy (no dummy moving)
      self.busy = False

   def setPosition(self, mMap, position):
      """
      Place the camera in a static position.

      mMap - the map to put it on.
      position - the position to put it on.
      """

      #not attached to any object
      self.attach = None

      #set our map and position
      self.map = mMap
      self.position = position

   def attachTo(self, mObject):
      """
      Attach the camera to an object, usually the player.

      The object must have map and position attributes, and a getMoveOffset() method.
      It should also be local to the player, as the player's location determines what maps are loaded.

      mObject - the object to attach to.
      """

      #set the object we're attached to
      self.attach = mObject

   def setNewWeather(self, weather):
      self.weather = weather
      if weather == W_DARK:
         self.overlay = DarknessOverlay(self.screen)
      elif weather == W_RAIN:
         self.overlay = RainOverlay(self.screen)
      elif weather == W_SAND:
         self.overlay = SandOverlay(self.screen)
      else:
         self.overlay = None

   def drawFrame(self):
      """Draw a frame to the screen"""

      #find the map, position and offset to use
      #if we're attached, use the map, position and offset of the object
      #if we're not attached, use our own map and position, with no offset
      if self.attach is not None:
         if self.dummy is not None:
            mMap = self.dummy.map
            position = self.dummy.position
            cameraOffset = self.dummy.getMoveOffset()
         else:
            mMap = self.attach.map
            position = self.attach.position
            cameraOffset = self.attach.getMoveOffset()
      else:
         mMap = self.map
         position = self.position
         cameraOffset = (0,0)

      #draw in all the tiles
      #iterate over each level, going over each coordinate and drawing in the required tiles
      #only draw the border tiles in once, on the first pass
      bordersDrawn = False
      switchSprites = []
      for level in range(0, 3):
            for x in range(-1, self.size[0]+1): #1 tile either side for when the object is moving halfway between tiles
               for y in range(-1, self.size[1]+1):

                  #convert the screen coordinates x, y into map coordinates
                  #if it's on the map, go through the map layers on the current level
                  #if they specify a tile in the current position, add it to our list of tiles to draw
                  reqTileLoc = position[0]-self.centre[0]+x, position[1]-self.centre[1]+y
                  reqTiles = []
                  if (reqTileLoc[0] >= 0) and (reqTileLoc[1] >= 0) and (reqTileLoc[0] < mMap.size[0]) and (reqTileLoc[1] < mMap.size[1]):
                     for layer in mMap.getLayersOnLevel(level):
                        i = layer[reqTileLoc]
                        if i >= 0: #if no tile is specified, this should be -1
                           reqTiles.append(mMap.tileset[i])

                  #otherwise start checking connected maps
                  #for each map, work out what the map coordinate would be on the map
                  #if it would be on that map, go through the layers on the current level
                  #if they specify a tile in the current position, add it to our list of tiles to draw
                  #if we did find one, stop looking for any more                  
                  else:
                     for direction, (con, offset) in list(mMap.connectedMaps.items()):
                        if direction == DIR_LEFT: 
                           rel = reqTileLoc[0]+con.size[0], reqTileLoc[1]-offset
                        elif direction == DIR_RIGHT:
                           rel = reqTileLoc[0]-mMap.size[0], reqTileLoc[1]-offset
                        elif direction == DIR_UP:
                           rel = reqTileLoc[0]-offset, reqTileLoc[1]+con.size[1]
                        elif direction == DIR_DOWN:
                           rel = reqTileLoc[0]-offset, reqTileLoc[1]-mMap.size[1]
                        if (0 <= rel[0] < con.size[0]) and (0 <= rel[1] < con.size[1]):
                           for layer in con.getLayersOnLevel(level):
                              i = layer[rel]
                              if i >= 0:
                                 reqTiles.append(con.tileset[i])
                           break

                  #if we've still not found a tile yet for this position, and borders haven't been drawn in yet,
                  #then get the border tile for the current position.
                  if (len(reqTiles) == 0) and not bordersDrawn:
                     reqTiles.append(mMap.tileset[mMap.getBorderTile(reqTileLoc)])

                  #blit the required tiles to the correct position
                  for t in reqTiles:
                     self.screen.blit(t, ((x*globs.TILESIZE[0])-cameraOffset[0], (y*globs.TILESIZE[1])-cameraOffset[1]))

            #having finished the first pass, any borders needed shold have been drawn by now
            bordersDrawn = True

            #draw the map's sprites
            #filtering them by level gives the ids, so use this to build a list of sprites
            #sort by y value so higher sprites are drawn first
            #for each sprite, find its screen coordinates and offset, and use these to draw it
            spriteIds = [a for a in mMap.sprites if mMap.sprites[a].level == level]
            sprites = [mMap.sprites[key] for key in spriteIds]
            if level == 0:
               sprites += mMap.objects
            sprites = sorted(sprites, key=lambda s: s.position[1])
            for s in sprites:
               if s.visible:
                  if not s.switch:
                     reqLoc = (s.position[0] - position[0] + self.centre[0]), (s.position[1] - position[1] + self.centre[1])
                     offset = s.getOffset()
                     pos = ((reqLoc[0]*globs.TILESIZE[0])+offset[0]-cameraOffset[0],
                            (reqLoc[1]*globs.TILESIZE[1])+offset[1]-cameraOffset[1])
                     self.screen.blit(s.getTile(), pos)
                     try:
                        if s.bubble is not None:
                           self.screen.blit(s.bubble, (pos[0]-((s.bubble.get_width()-globs.TILESIZE[0])/2), pos[1]-s.bubble.get_height()))
                     except AttributeError:
                        pass
                  else:
                     switchSprites.append(s)

            #draw the sprites from connecting maps
            #use the same process as before
            for direction, (con, offset) in list(mMap.connectedMaps.items()):
               spriteIds = [a for a in con.sprites if con.sprites[a].level == level]
               sprites = [con.sprites[x] for x in spriteIds]
               if level == 0:
                  sprites += con.objects
               sprites = sorted(sprites, key=lambda s: s.position[1])
               for s in sprites:
                  if s.visible:
                     if direction == DIR_LEFT: 
                        rel = s.position[0]-con.size[0], s.position[1]+offset
                     elif direction == DIR_RIGHT:
                        rel = s.position[0]+mMap.size[0], s.position[1]+offset
                     elif direction == DIR_UP:
                        rel = s.position[0]+offset, s.position[1]-con.size[1]
                     elif direction == DIR_DOWN:
                        rel = s.position[0]+offset, s.position[1]+mMap.size[1]
                     reqLoc = (rel[0] - position[0] + self.centre[0]), (rel[1] - position[1] + self.centre[1])
                     spriteOffset = s.getOffset()
                     self.screen.blit(s.getTile(), ((reqLoc[0]*globs.TILESIZE[0])+spriteOffset[0]-cameraOffset[0],
                                                    (reqLoc[1]*globs.TILESIZE[1])+spriteOffset[1]-cameraOffset[1]))

      for s in switchSprites:
         reqLoc = (s.position[0] - position[0] + self.centre[0]), (s.position[1] - position[1] + self.centre[1])
         offset = s.getOffset()
         self.screen.blit(s.getTile(), ((reqLoc[0]*globs.TILESIZE[0])+offset[0]-cameraOffset[0],
                                        (reqLoc[1]*globs.TILESIZE[1])+offset[1]-cameraOffset[1]))

      if mMap.weather != self.weather:
         self.setNewWeather(mMap.weather)
      
      if self.overlay is not None:
         self.overlay.draw()

   def tick(self):
      """Tick the camera."""

      #if we have a dummy, tick it
      #set our own busy status to that of the dummy
      if self.dummy is not None:
         self.dummy.tick()
         self.busy = self.dummy.busy

      #if there's an overlay, tick it
      if self.overlay is not None:
         self.overlay.tick()

   def command_startDynamic(self, speed=1):
      """
      Prepare for dynamic camera movement.

      speed - the speed of the movement.
      """

      #create a dummy and set its speed
      self.dummy = DummySprite(self.attach.map, self.attach.position)
      self.dummy.speed = speed
      
   def command_endDynamic(self):
      """
      Return to normal camera mode.
      """

      #destroy the dummy
      self.dummy = None

   def command_move(self, stepString):
      """
      Move the camera dynamically.

      Must follow a startDynamic() command.

      stepString - a string of comma separated step instructions.
      """

      #convert the string into a list of instructions
      try:
         steps = [STEPNAMES[n.strip()] for n in stepString.split(",")]
      except KeyError as e:
         raise script_engine.DInvalidArgError("move", stepString, "unrecognised step instruction: %s" % str(e))

      #start the dummy moving on the first step, and add any others to its queue
      self.dummy.move(steps[0])
      self.dummy.stepQueue += steps[1:]

   def command_flash(self):
      if self.overlay is not None:
         self.overlay.flash()

class DummySprite():
   """Dummy sprite class allowing dynamic camera movement."""
   
   def __init__(self, mMap, position):
      """
      Set up the dummy.

      mMap - the map the dummy is on.
      position - the initial position.
      """

      #set map and position attributes
      self.map = mMap
      self.position = position

      #set speed to 1 (walk)
      self.speed = 1

      #initialise movement variables
      self.walkCycle = 0
      self.destination = self.position
      self.direction = DIR_UP
      self.stepQueue = []

      #we're not busy yet
      self.busy = False

   def getMoveOffset(self):
      """Calculate the offset due to movement of the dummy."""

      #depending on the direction, calculate the offset, splitting tiles into 8 steps
      if self.direction == DIR_UP:
         return 0, (-1*self.walkCycle*globs.TILESIZE[1])/8
      elif self.direction == DIR_DOWN:
         return 0, (self.walkCycle*globs.TILESIZE[1])/8
      elif self.direction == DIR_LEFT:
         return (-1*self.walkCycle*globs.TILESIZE[0])/8, 0
      elif self.direction == DIR_RIGHT:
         return (self.walkCycle*globs.TILESIZE[0])/8, 0

   def tick(self):
      """Tick the dummy."""

      #if we're in the middle of a step, advance the walk cycle
      if self.busy:
         self.walkCycle += self.speed

         #if this finishes a step, update the position of the dummy, and reset walk cycle
         #if there is another step to take, start it off, else we're not busy anymore
         if self.walkCycle >= 8:
            self.position = self.destination
            self.walkCycle = 0

            if self.stepQueue:
               nextDir = self.stepQueue.pop(0)
               self.move(nextDir)
            else:
               self.busy = False

   def move(self, direction):
      """
      Move the dummy in a given direction.

      direction - the direction to move.
      """

      #set our direction, and calculate the destination tile
      #set ourselves as busy to start moving
      self.direction = direction
      if direction == DIR_UP:
         self.destination = self.position[0], self.position[1]-1
      elif direction == DIR_DOWN:
         self.destination = self.position[0], self.position[1]+1
      elif direction == DIR_LEFT:
         self.destination = self.position[0]-1, self.position[1]
      elif direction == DIR_RIGHT:
         self.destination = self.position[0]+1, self.position[1]
      self.busy = True











         
