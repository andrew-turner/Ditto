import os

from . import objects
from . import settings
from . import data
from . import globs
from . import tileset
from . import script_engine
from . import sprite
from . import sound
import eng.error as error

removableObjects = {}
pushableObjects = {}

def init():
   objRoot = data.getTreeRoot(globs.OBJECTS)
   for objectNode in objRoot.getChildren("removable"):
      removableObjects[objectNode.getAttr("type", data.D_STRING)] = objectNode
   for objectNode in objRoot.getChildren("pushable"):
      pushableObjects[objectNode.getAttr("type", data.D_STRING)] = objectNode

def createObject(objectNode, mMap):
   objType = objectNode.getAttr("type", data.D_STRING)
   
   if objType in removableObjects:
      node = removableObjects[objType]
      return RemovableObject(node, mMap, tuple(objectNode.getAttr("position", data.D_INT2LIST)))

   elif objType in pushableObjects:
      node = pushableObjects[objType]
      return PushableObject(node, mMap, tuple(objectNode.getAttr("position", data.D_INT2LIST)))

   else:
      raise error.DevError("Invalid object type: {}".format(objType))

class RemovableObject(objects.VisibleObject):
   def __init__(self, node, mMap, position):
      objects.VisibleObject.__init__(self)

      self.map = mMap
      self.position = position

      tsId = node.getAttr("tileset", data.D_STRING)
      self.tileset = tileset.Tileset(tsId)

      self.scriptEngine = script_engine.ScriptEngine()

      scriptNode = node.getChild("script")
      self.script = script_engine.scriptFromNode(scriptNode)

      self.scriptCommands["remove"] = self.command_remove
      self.removeAfterAnim = False

   def getOffset(self):
      return self.tileset.tileOffset

   def onInvestigate(self):
      if not self.removeAfterAnim:
         self.scriptEngine.run(self.script, self)

   def command_remove(self, animName=None):
      if animName is not None:
         try:
            a = self.tileset.scriptAnimations[animName]
         except KeyError:
            pass #error
         self.animation = a
         a.play(False)
         self.removeAfterAnim = True
      else:
         self.map.objects.remove(self)

   def tick(self):
      objects.VisibleObject.tick(self)

      if self.removeAfterAnim:
         if not self.animation.active:
            self.map.objects.remove(self)

class PushableObject(objects.VisibleObject):
   def __init__(self, node, mMap, position):
      objects.VisibleObject.__init__(self)

      self.map = mMap
      self.position = position

      tsId = node.getAttr("tileset", data.D_STRING)
      self.tileset = tileset.Tileset(tsId)

      self.scriptEngine = script_engine.ScriptEngine()

      scriptNode = node.getChild("script")
      self.script = script_engine.scriptFromNode(scriptNode)

      self.direction = sprite.DIR_UP
      self.walkCycle = 0
      self.busy = False

   def move(self, direction):
      self.direction = direction
      if not self.busy:
         if direction == sprite.DIR_UP:
            self.destination = self.position[0], self.position[1]-1
         elif direction == sprite.DIR_DOWN:
            self.destination = self.position[0], self.position[1]+1
         elif direction == sprite.DIR_LEFT:
            self.destination = self.position[0]-1, self.position[1]
         elif direction == sprite.DIR_RIGHT:
            self.destination = self.position[0]+1, self.position[1]

         self.busy = True
         sound.playEffect(sound.SD_PUSH)
         self.map.walkonto(self, self.destination)


   def getMoveOffset(self):
      if self.direction == sprite.DIR_UP:
         return 0, (-1*self.walkCycle*globs.TILESIZE[1])/8
      elif self.direction == sprite.DIR_DOWN:
         return 0, (self.walkCycle*globs.TILESIZE[1])/8
      elif self.direction == sprite.DIR_LEFT:
         return (-1*self.walkCycle*globs.TILESIZE[0])/8, 0
      elif self.direction == sprite.DIR_RIGHT:
         return (self.walkCycle*globs.TILESIZE[0])/8, 0

   def getOffset(self):
      moveOffset = self.getMoveOffset()
      return self.tileset.tileOffset[0]+moveOffset[0], self.tileset.tileOffset[1]+moveOffset[1]

   def onInvestigate(self):
      self.scriptEngine.run(self.script, self)

   def tick(self):
      if self.busy:
         self.walkCycle += 1
         if self.walkCycle >= 8:
            self.position = self.destination
            self.walkCycle = 0

            if self.position in self.map.reservedPositions:
               self.map.reservedPositions.pop(self.position)

            self.busy = False
