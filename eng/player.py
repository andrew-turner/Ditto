import os

from . import tileset
from . import tilemap
from . import settings
from . import animation
from . import sprite
from . import pokemon
from . import items
from . import sound
from . import data
from . import error
from . import script_engine

STATUSNAMES = {"run": sprite.S_RUN,
               "surf": sprite.S_TERRAIN}

class Player(sprite.Sprite):
   """Class representing the player."""
   
   def __init__(self, node, mMap, position, level):
      """
      Set up the player.

      node - the <player> node.
      mMap - the map to start on.
      position - the position to start at.
      level - the level to start on.
      """

      #init the sprite
      sprite.Sprite.__init__(self, node, mMap, position, level)

      #create status tilesets
      self.statusTilesets = {}
      self.statusTilesets[sprite.S_WALK] = self.tileset
      for statusNode in node.getChildren("status"):
         try:
            status = STATUSNAMES[statusNode.getAttr("name", data.D_STRING)]
         except KeyError:
            raise data.DInvalidAttributeError(statusNode, "name")
         tsId = statusNode.getAttr("tileset", data.D_STRING)
         ts = tileset.Tileset(tsId)
         self.statusTilesets[status] = ts

      #set up scripting     
      self.scriptCommands["surf"] = self.command_surf
      self.scriptCommands["climbWaterfall"] = self.command_climbWaterfall
      self.scriptCommands["warp"] = self.command_warp

      self.name = None

   def walk(self, direction, force=False, isPlayer=True):
      sprite.Sprite.walk(self, direction, force, True)

      if (self.destination[0] < 0) and self.busy:
            hold = self.map
            con = self.map.connectedMaps[sprite.DIR_LEFT][0]
            offset = self.map.connectedMaps[sprite.DIR_LEFT][1]
            self.position = self.position[0]+con.size[0], self.position[1]-offset
            self.destination = self.position[0]-1, self.position[1]
            self.map = con
            hold.connectedMaps = {}
            self.map.loadConnections()
            self.map.connectedMaps[sprite.DIR_RIGHT] = (hold, -1*offset)
            del(hold.sprites["PLAYER"])
            self.map.sprites["PLAYER"] = self
            sound.playMusic(self.map.music)
      elif (self.destination[0] >= self.map.size[0]) and self.busy:
            hold = self.map
            con = self.map.connectedMaps[sprite.DIR_RIGHT][0]
            offset = self.map.connectedMaps[sprite.DIR_RIGHT][1]
            self.position = self.position[0]-self.map.size[0], self.position[1]-offset
            self.destination = self.position[0]+1, self.position[1]
            self.map = con
            hold.connectedMaps = {}
            self.map.loadConnections()
            self.map.connectedMaps[sprite.DIR_LEFT] = (hold, -1*offset)
            del(hold.sprites["PLAYER"])
            self.map.sprites["PLAYER"] = self
            sound.playMusic(self.map.music)
      elif (self.destination[1] < 0) and self.busy:
            hold = self.map
            con = self.map.connectedMaps[sprite.DIR_UP][0]
            offset = self.map.connectedMaps[sprite.DIR_UP][1]
            self.position = self.position[0]-offset, self.position[1]+con.size[1]
            self.destination = self.position[0], self.position[1]-1
            self.map = con
            hold.connectedMaps = {}
            self.map.loadConnections()
            self.map.connectedMaps[sprite.DIR_DOWN] = (hold, -1*offset)
            del(hold.sprites["PLAYER"])
            self.map.sprites["PLAYER"] = self
            sound.playMusic(self.map.music)
      elif (self.destination[1] >= self.map.size[1]) and self.busy:
            hold = self.map
            con = self.map.connectedMaps[sprite.DIR_DOWN][0]
            offset = self.map.connectedMaps[sprite.DIR_DOWN][1]
            self.position = self.position[0]-offset, self.position[1]-self.map.size[1]
            self.destination = self.position[0], self.position[1]+1
            self.map = con
            hold.connectedMaps = {}
            self.map.loadConnections()
            self.map.connectedMaps[sprite.DIR_UP] = (hold, -1*offset)
            del(hold.sprites["PLAYER"])
            self.map.sprites["PLAYER"] = self
            sound.playMusic(self.map.music)

   def transferTo(self, mMap, position):
      del(self.map.sprites["PLAYER"])
      self.map.connectedMaps = {}

      oldWeather = self.map.weather
      
      self.map = mMap
      self.position = position

      self.map.sprites["PLAYER"] = self
      self.map.loadConnections()

      sound.playMusic(self.map.music)

   def setRunning(self, isRunning):
      if (self.status in (sprite.S_WALK, sprite.S_RUN)) and not self.sliding:
         if isRunning:
            self.setStatus(sprite.S_RUN)
            self.speed = 2
         else:
            self.setStatus(sprite.S_WALK)
            self.speed = 1

   def command_surf(self):
      self.setStatus(sprite.S_TERRAIN)
      self.walkForward(True, True)

   def command_climbWaterfall(self):
      self.climbingWaterfall = True
      self.walk(sprite.DIR_UP, True, True)

   def getVar(self, name):
      if name == "level":
         return self.level
      elif name == "direction":
         if self.direction == sprite.DIR_UP:
            return "UP"
         elif self.direction == sprite.DIR_DOWN:
            return "DOWN"
         elif self.direction == sprite.DIR_LEFT:
            return "LEFT"
         elif self.direction == sprite.DIR_RIGHT:
            return "RIGHT"
      elif name == "isSurfing":
         return (self.status == sprite.S_TERRAIN)
      else:
         raise script_engine.DLookupError(name)

   def setVar(self, name, val):
      if name == "level":
         self.level = val
      else:
         raise script_engine.DLookupError(name)

   def investigate(self):
      """Investigate the position in front of the player."""

      #find the target position, and have the map investigate it
      if self.direction == sprite.DIR_UP:
         target = self.position[0], self.position[1]-1
      elif self.direction == sprite.DIR_DOWN:
         target = self.position[0], self.position[1]+1
      elif self.direction == sprite.DIR_LEFT:
         target = self.position[0]-1, self.position[1]
      elif self.direction == sprite.DIR_RIGHT:
         target = self.position[0]+1, self.position[1]  
      self.map.investigate(target, self.level)

   def command_warp(self, mapId, position):
      mMap = tilemap.Tilemap(mapId)
      self.transferTo(mMap, list(map(int, position.split(","))))
      self.destination = self.getPositionInFront()
      self.level = 0
