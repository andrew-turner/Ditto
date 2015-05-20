import os
import xml.etree.ElementTree as ET

from . import settings
from . import tileset
from . import camera
from . import npc
from . import trainer
from . import script_engine
from . import events
from . import error
from . import data
from . import globs
from . import sound
from . import environment_objects
import eng.behaviours as behaviours
import eng.movement as movement
import eng.resource_ids as resource_ids

from eng.constants.weather import *
from eng.constants.directions import *
from eng.constants.behaviours import *

#border tile locations
BD_NW = 0
BD_NE = 1
BD_SW = 2
BD_SE = 3
            
class Layer():
   """Class to represent a single layer of a map."""
   
   def __init__(self):
      """
      Create a blank layer, which must be populated by calling some kind of opening function.
      """

      #create initial tile array and animation dictionary for walkonto animations 
      self.array = []
      self.animations = {}

   def openTMXNode(self, layerNode):
      """
      Use a <layer> node from a TMX file to create the layer data.

      layerNode - the TMX <layer> node
      """
      
      #find the level
      self.level = None
      props = layerNode.find("properties")
      if props is None:
         raise error.DInvalidResourceError("Unknown TMX file", "No layer properties defined.")
      for p in props.getchildren():
         if p.attrib["name"] == "level":
            try:
               self.level = int(p.attrib["value"])
            except ValueError:
               raise error.DInvalidResourceError("Unknown TMX file", "Level is not an integer.")
            break
      if self.level is None:
         raise error.DInvalidResourceError("Unknown TMX file", "Layer property \"level\" is not defined.")

      #get hold of the data
      data = layerNode.find("data")

      #if it's csv encoded, simply split into lines,
      #and split each line into tiles which can be added to the array
      if data.attrib["encoding"] == "csv":
         lines = data.text.split("\n")
         for line in lines:
            if line != "":
               listed = line.split(",")
               listed = [a for a in listed if a != ""] #remove any blank elements
               row = [int(a)-1 for a in listed] #TMX indexes start at 1, we start at 0
               self.array.append(row)
      else:
         raise error.DittoUnsupportedException("Unknown TMX file", "TMX layer encoding", data.attrib["encoding"])

   def offsetElements(self, i):
      """
      Subtract an amount from each element in the tile array.

      Used to correct for multiple tilesets being offset by TMX format.

      i - the amount to subtract
      """

      #iterate over each tile and subtract
      #if the value is -1, indicating a blank tile, leave it as that
      for y in range(0, len(self.array)):
         for x in range(0, len(self.array[0])):
            if self.array[y][x] != -1:
               self.array[y][x] -= i

   def tick(self):
      """
      Update the map by one frame.

      Updates all the animations currently active on the map.
      """

      #tick each animation, and remember any animations which have finished
      #remove any finished ones from the dictionary
      finished = []
      for key, anim in list(self.animations.items()):
         anim.tick()
         if not anim.active:
            finished.append(key)      
      for key in finished:
         self.animations.pop(key)

   def __getitem__(self, position):
      """
      Returns the tile at the position given.

      If the tile is animated, returns the correct animation frame.

      position - the x,y position coordinate to get.
      """

      #if the tile is animated, get the animation frame
      #otherwise just grab the required tile from the array
      if position in self.animations:
         t = self.animations[position].currentFrame
      else:
         t = self.array[position[1]][position[0]]
      return t

class Tilemap(script_engine.ScriptableObject):
   """
   Class representing a map object.
   """
   
   def __init__(self, mapId):
      """
      Open the map data file, set border tiles and connections, and add NPCs and other events.

      mapId - the map's id.
      """

      #for the scripting engine
      script_engine.ScriptableObject.__init__(self)
      self.scriptCommands["playAnim"] = self.command_playAnim

      #store variables we'll need later
      self.id = mapId
      self.fn = resource_ids.getMapFn(mapId)

      #get a script engine (singleton)
      self.scriptEngine = script_engine.ScriptEngine()

      #parse the XML file
      root = data.getTreeRoot(self.fn)
      self.name = root.getOptionalAttr("name", data.D_STRING)
      self.music = os.path.join(settings.path, "data", root.getAttr("music", data.D_STRING))

      #check that ids match
      if root.getAttr("id", data.D_STRING) != self.id:
         raise error.DevError("Map id incorrect.",
                              "Map pointed by id \"{}\" considers it's id to be \"{}\".".format(self.id, root.getAttr("id", data.D_STRING)))

      #open the actual map data file to create the map tile data
      mapPath = os.path.join(settings.path, "data", root.getAttr("file", data.D_STRING))
      self.openMap(mapPath)

      #create the tileset
      tsId = root.getAttr("tileset", data.D_STRING)
      self.tileset = tileset.Tileset(tsId)

      #set the border tiles
      self.borderTiles = {}
      borderNode = root.getChild("border")

      #set each border node with the correct tile indexes, subtracting 1 because the tileset starts at 1 not 0
      self.borderTiles[BD_NW] = borderNode.getAttr("nw", data.D_INT)-1
      self.borderTiles[BD_NE] = borderNode.getAttr("ne", data.D_INT)-1
      self.borderTiles[BD_SW] = borderNode.getAttr("sw", data.D_INT)-1
      self.borderTiles[BD_SE] = borderNode.getAttr("se", data.D_INT)-1

      #get weather data
      weatherNode = root.getOptionalChild("weather")
      if weatherNode is not None:
         weatherName = weatherNode.getAttr("type", data.D_STRING)
         try:
            self.weather = WEATHERNAMES[weatherName]
         except KeyError:
            raise KeyError
      else:
         self.weather = W_NONE

      #script default file
      self.scriptDefault = root.getChild("scriptfile").getAttr("source", data.D_FILENAME)

      #environment data
      self.environment = root.getOptionalAttr("environment", data.D_STRING, "FIELD")
      
      #create any connections from the map
      #connected maps will not be loaded until the map becomes the main game map
      #connections are stored as {direction: (filename, offset)}
      self.connections = {}
      self.connectedMaps = {}
      for c in root.getChildren("connection"):
         side = c.getAttr("side", data.D_STRING)
         conId = c.getAttr("map", data.D_STRING)
         offset = c.getAttr("offset", data.D_INT)
         
         if side == "left":
            self.connections[DIR_LEFT] = (conId, offset)
         elif side == "right":
            self.connections[DIR_RIGHT] = (conId, offset)
         elif side == "up":
            self.connections[DIR_UP] = (conId, offset)
         elif side == "down":
            self.connections[DIR_DOWN] = (conId, offset)

      #create any NPCs, adding them to the sprite dictionary
      self.sprites = {}
      for n in root.getChildren("npc"):
         spr = npc.NPC(n, self)
         self.sprites[spr.id] = spr

      #create any trainers
      #for trainerNode in root.getChildren("trainer"):
      #   spr = trainer.Trainer(trainerNode, self)
      #   self.sprites[spr.id] = spr

      #create a dictionary to hold positions reserved by moving sprites
      self.reservedPositions = {}

      #create objects
      self.objects = []
      for objectNode in root.getChildren("object"):
         obj = environment_objects.createObject(objectNode, self)
         self.objects.append(obj)
      self.strengthActive = False
      
      #create script and warp events, adding them to the events dictionary
      #if a load script is defined, create it
      self.events = {}
      loadScript = None
      for s in root.getChildren("script"):
         trigger = s.getAttr("trigger", data.D_STRING)
         if trigger == "load":
            loadScript = script_engine.scriptFromNode(s, self.scriptDefault)   
         else:
            position = tuple(s.getAttr("position", data.D_INT2LIST)) 
            self.events[position] = events.ScriptEvent(s, self)
            
      for w in root.getChildren("warp"):
         position = tuple(w.getAttr("position", data.D_INT2LIST))
         self.events[position] = events.Warp(w, self)

      #if there is a load script, run it
      if loadScript is not None:
         self.scriptEngine.run(loadScript, self)

   def openMap(self, fn):
      ext = os.path.splitext(fn)[1]
      if ext == ".tmx":
         self.openTMX(fn)
      else:
         raise error.DittoUnsupportedException("map data extension", ext)

   def openTMX(self, fn):
      """
      Open a TMX file and use it to set map size and create tile layers and a collision layer.

      fn - the filename of the TMX file.
      """

      #parse the TMX XML markup
      try:
         tree = ET.parse(fn)
      except FileNotFoundError:
         raise error.DevError("TMX file not found:",
                              fn,
                              "While opening map \"{}\" with file:".format(self.id),
                              self.fn)
      root = tree.getroot()
      self.size = int(root.attrib["width"]), int(root.attrib["height"])

      #find the offset at which the collision and behaviour layers tile data is stored
      collisionTilesetOffset = None
      behaviourTilesetOffset = None
      for ts in root.findall("tileset"):
         if ts.attrib["name"] == "collision":
            collisionTilesetOffset = int(ts.attrib["firstgid"])-1
         elif ts.attrib["name"] == "behaviour":
            behaviourTilesetOffset = int(ts.attrib["firstgid"])-1
      if collisionTilesetOffset is None:
         raise error.DittoInvalidResourceException(fn, "Collision tileset")
      if behaviourTilesetOffset is None:
         raise error.DittoInvalidResourceException(fn, "Behaviour tileset")

      #create each layer, separating the collision and behaviour data
      self.layers = []
      self.collisionLayer = None
      self.behaviourLayer = None
      for layer in root.findall("layer"):
         l = Layer()
         l.openTMXNode(layer)
         if l.level == -1: #collision layer indicated by level == -1
            self.collisionLayer = l
         elif l.level == -2:
            self.behaviourLayer = l
         else:
            self.layers.append(l)
      if self.collisionLayer is None:
         raise error.DittoInvalidResourceException(fn, "Collision data layer")
      if self.behaviourLayer is None:
         raise error.DittoInvalidResourceException(fn, "Behaviour data layer")

      #compensate for tilesets not starting at 1
      self.collisionLayer.offsetElements(collisionTilesetOffset)
      self.behaviourLayer.offsetElements(behaviourTilesetOffset)

   def getLayersOnLevel(self, i):
      """
      Return a list of layers on this map on a given level.

      i - the level to look on.
      """

      #return a filtered copy of the map's layers
      return [a for a in self.layers if a.level == i]

   def getBorderTile(self, position):
      """
      Return the index of the border tile at a position.

      position - the position of the tile on the map
      """

      #determine the tiles position in the border, and return the relevant tile index
      borderPosition = (position[0]%2, position[1]%2)
      if borderPosition == (0,0):
         return self.borderTiles[BD_NW]
      elif borderPosition == (1,0):
         return self.borderTiles[BD_NE]
      elif borderPosition == (0,1):
         return self.borderTiles[BD_SW]
      elif borderPosition == (1,1):
         return self.borderTiles[BD_SE]

   def walkonto(self, spr, destination, isPlayer=False):
      """
      Deal with a sprite walking onto a tile, by animating if required and reserving the position.

      spr - the sprite which is walking onto the tile.
      destination - the tile they're walking onto.
      """

      #if the destination is on the map, check the sprite's layer for walkonto animations
      #if there are any, play them
      #then reserve the position
      if (0 <= destination[0] < self.size[0]) and (0 <= destination[1] < self.size[1]):
         layers = self.getLayersOnLevel(spr.level)
         for l in layers:
            tile = l[destination]
            if tile in self.tileset.walkontoAnimations:
               l.animations[destination] = self.tileset.walkontoAnimations[tile]
               l.animations[destination].play(False)
         self.reservedPositions[destination] = spr

      #if it's a player, check for events and deal with any
      if isPlayer:
         if destination in self.events:
            s = self.events[destination]
            if s.trigger == events.EV_WALKONTO:
               s.activate()
               return
         
         b = self.getBehaviourData(destination)
         if b in behaviours.BUILTINBEHAVIOURS:
            builtin = behaviours.BUILTINBEHAVIOURS[b]
            if builtin == B_SLIDE:
               spr.slide()
               return
            elif builtin in (B_LEDGEDOWN, B_LEDGELEFT, B_LEDGERIGHT):
               spr.ledge()
               return
            elif builtin == B_WATERFALL:
               if spr.climbingWaterfall:
                  spr.stepQueue.append(DIR_UP)
                  spr.switch = True
               else:
                  spr.stepQueue.append(DIR_DOWN)
                  spr.switch = True
            elif builtin == B_FORCEDOWN:
               spr.forceTile(DIR_DOWN)
            elif builtin == B_FORCEUP:
               spr.forceTile(DIR_UP)
            elif builtin == B_FORCELEFT:
               spr.forceTile(DIR_LEFT)
            elif builtin == B_FORCERIGHT:
               spr.forceTile(DIR_RIGHT)
               
         for spriteId in self.sprites:
            spr1 = self.sprites[spriteId]
            if isinstance(spr1, trainer.Trainer):
               if spr1.checkPosition(destination):
                  spr1.activate()
               

   def loadConnections(self):
      """
      Load all the connecting maps.

      Called when the map becomes the main game map.
      """

      #create each connecting map
      for direction, (conId, offset) in list(self.connections.items()):
         self.connectedMaps[direction] = (Tilemap(conId), offset)

   def getCollisionData(self, position):
      """
      Get the collision tile index at a given position.

      position - the position to use.
      """
      
      #if it's on the map, simply return the collision data
      if (0 <= position[0] < self.size[0]) and (0 <= position[1] < self.size[1]):
         return self.collisionLayer.array[position[1]][position[0]] #direct indexing prevents checking for animations

      #otherwise see if it's on a connecting map
      #if it is, get it
      else:
         for key in self.connectedMaps:
            con = self.connectedMaps[key][0]
            offset = self.connectedMaps[key][1]
            if key == DIR_LEFT: 
               rel = position[0]+con.size[0], position[1]-offset
            elif key == DIR_RIGHT:
               rel = position[0]-self.size[0], position[1]-offset
            elif key == DIR_UP:
               rel = position[0]-offset, position[1]+con.size[1]
            elif key == DIR_DOWN:
               rel = position[0]-offset, position[1]-self.size[1]
            if (0 <= rel[0] < con.size[0]) and (0 <= rel[1] < con.size[1]):
               return con.getCollisionData(rel)

      #else it must be a border tile, return 1 (block)      
      return 1

   def getBehaviourData(self, position):
      """
      Get the behaviour value at a given position.

      position - the position to use.
      """

      #if the position is on this map, return the relevant data
      if (0 <= position[0] < self.size[0]) and (0 <= position[1] < self.size[1]):
         return self.behaviourLayer.array[position[1]][position[0]] #direct indexing prevents checking for animations

      #otherwise see if it's on a connecting map
      #if it is, get it
      else:
         for key in self.connectedMaps:
            con = self.connectedMaps[key][0]
            offset = self.connectedMaps[key][1]
            if key == DIR_LEFT: 
               rel = position[0]+con.size[0], position[1]-offset
            elif key == DIR_RIGHT:
               rel = position[0]-self.size[0], position[1]-offset
            elif key == DIR_UP:
               rel = position[0]-offset, position[1]+con.size[1]
            elif key == DIR_DOWN:
               rel = position[0]-offset, position[1]-self.size[1]
            if (0 <= rel[0] < con.size[0]) and (0 <= rel[1] < con.size[1]):
               return con.getBehaviourData(rel)

      #else it must be a border tile, return -1 (no behaviour)      
      return -1

   def emptyAt(self, position, allowPushing=True):
      """
      Find out whether a given position is empty and available.

      position - the position to use.
      direction - the direction the sprite would be walking. (For pushing)
      allowPushing - whether pushables can be pushed to make the position empty
      """

      #check for any sprites at the position
      for key in self.sprites:
         s = self.sprites[key]
         if s.position == position and s.visible: #not visible means it isn't taking up the tile
            return False

      #check whether the position is reserved   
      for pos in self.reservedPositions:
         if pos == position:
            return False

      #check for objects blocking
      for obj in self.objects:
         if obj.position == position:
            return False

      #if nothing found, it must be empty   
      return True

   def getSpriteById(self, spriteId):
      """
      Get a given sprite by it's id.

      spriteId - the id of the sprite to find.
      """

      #find the required sprite
      return self.sprites[spriteId]

   def getPushableAt(self, position):
      for obj in self.objects:
         if (obj.position == position) and isinstance(obj, environment_objects.PushableObject):
            return obj
      else:
         return None

   def getObject(self, name):
      if name == "tileset":
         return self.tileset
      else:
         return self.getSpriteById(name)

   def command_playAnim(self, name, x, y):
      l = self.layers[-1]
      position = (x,y)
      l.animations[position] = self.tileset.scriptAnimations[name]
      l.animations[position].play(False)      

   def investigate(self, target, level):
      """
      Called by a player to investigate a map for events.

      target - the position to look at
      level - the level to look on
      """

      #check for sprites on the position and level
      #if one is found, call its onInvestigate method
      spriteIds = [a for a in self.sprites if self.sprites[a].level == level]
      sprites = [self.sprites[x] for x in spriteIds]
      for s in sprites:
         if s.position == target and s.visible:
            s.onInvestigate()
            return

      #next check for objects
      for obj in self.objects:
         if obj.position == target:
            obj.onInvestigate()
            return

      #if there was no sprite, check for any events triggered on investigate   
      if target in self.events:
         if self.events[target].trigger == events.EV_INVESTIGATE:
            self.events[target].activate()
            return

      #finally, check for a behaviour byte and process that
      b = self.getBehaviourData(target)
      col = self.getCollisionData(target)
      action, targetLevel = movement.getActionLevel(col)
      if (targetLevel == level) and (action != movement.BRIDGE):
         self.processBehaviour(b, events.EV_INVESTIGATE)

   def processBehaviour(self, b, trigger, caller=None):
      if trigger == events.EV_INVESTIGATE:
         try:
            s = behaviours.BEHAVIOURSCRIPTS_INVESTIGATE[b]
            self.scriptEngine.run(s, self)
         except KeyError:
            pass

      elif trigger == events.EV_WALKONTO:
         try:
            s = behviours.BEHAVIOURSCRIPTS_WALKONTO[b]
            self.scriptEngine.run(s, self)
         except KeyError:
            pass

      elif trigger == events.EV_FINISHWALKONTO:
         try:
            builtin = behaviours.BUILTINBEHAVIOURS[b]
            if builtin == B_SLIDE:
               caller.walkForward()            
         except KeyError:
            caller.sliding = False
            caller.speed = 1         
      
   def tick(self):
      """Update the map one frame"""

      #we don't need to do anything, just tick our components
      self.tileset.tick()
      for l in self.layers:
         l.tick()
      for key in self.sprites:
         self.sprites[key].tick()
      for obj in self.objects:
         obj.tick()
      for key in self.connectedMaps:
         self.connectedMaps[key][0].tick()

   def getVar(self, name):
      if name == "strengthActive":
         return self.strengthActive
      else:
         raise script_engine.DLookupError(name)

   def setVar(self, name, val):
      if name == "strengthActive":
         self.strengthActive = bool(val)
      else:
         raise script_engine.DLookupError(name)

   def __repr__(self):
      return "<tilemap \"{}\">".format(self.id)

