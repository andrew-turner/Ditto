import os
import xml.etree.ElementTree as ET

from tkinter import *

import modules.tileset as tileset
from modules.utils import getGameDir

#icon filenames
NPC_ICON = "npc_icon.gif"
WARP_ICON = "warp_icon.gif"
SCRIPT_ICON = "script_icon.gif"
OBJECT_ICON = "object_icon.gif"


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

   def openTMXNode(self, layerNode):
      """
      Use a <layer> node from a TMX file to create the layer data.

      layerNode - the TMX <layer> node
      """
      
      #find the level
      self.level = None
      props = layerNode.find("properties")
      if props is None:
         raise ValueError
      for p in props.getchildren():
         if p.attrib["name"] == "level":
            try:
               self.level = int(p.attrib["value"])
            except ValueError:
               raise ValueError
            break
      if self.level is None:
         raise ValueError

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
         raise ValueError

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

   def __getitem__(self, position):
      """
      Returns the tile at the position given.

      position - the x,y position coordinate to get.
      """

      #otherwise just grab the required tile from the array
      t = self.array[position[1]][position[0]]
      return t

class Tilemap():
   """
   Class representing a map object.
   """
   
   def __init__(self, xmlFn):
      """
      Open the map data file, set border tiles and connections, and add NPCs and other events.

      fn - the map's fn.
      """

      #store variables we'll need later
      self.xmlFn = xmlFn
      self.gameDir = getGameDir(self.xmlFn)

      #parse the XML file
      tree = ET.parse(self.xmlFn)
      self.root = tree.getroot()

      #open the actual map data file to create the map tile data
      try:
         filename = self.root.attrib["file"]
      except KeyError:
         raise KeyError
      self.mapFn = os.path.join(self.gameDir, "data", filename)
      self.openMap(self.mapFn)

      #create the tileset
      self.tsFn = self.root.attrib["tileset"]
      self.tileset = tileset.Tileset(self.tsFn, self.gameDir)
      self.tileSize = self.tileset.tileSize

      #set the border tiles
      self.borderTiles = {}
      borderNode = self.root.find("border")

      #set each border node with the correct tile indexes, subtracting 1 because the tileset starts at 1 not 0
      if borderNode is not None:
         self.borderTiles[BD_NW] = int(borderNode.attrib["nw"])-1
         self.borderTiles[BD_NE] = int(borderNode.attrib["ne"])-1
         self.borderTiles[BD_SW] = int(borderNode.attrib["sw"])-1
         self.borderTiles[BD_SE] = int(borderNode.attrib["se"])-1

      #icons
      self.tiles = {}
      fn = os.path.join(os.getcwd(), "assets", NPC_ICON)
      self.tiles["npc"] = PhotoImage(file=fn)
      fn = os.path.join(os.getcwd(), "assets", WARP_ICON)
      self.tiles["warp"] = PhotoImage(file=fn)
      fn = os.path.join(os.getcwd(), "assets", SCRIPT_ICON)
      self.tiles["script"] = PhotoImage(file=fn)
      fn = os.path.join(os.getcwd(), "assets", OBJECT_ICON)
      self.tiles["object"] = PhotoImage(file=fn)

      self.events = {}

      #create any NPCs, adding them to the sprite dictionary
      #self.sprites = {}
      #for n in root.getChildren("npc"):
      #   spr = npc.NPC(n, self)
      #   self.sprites[spr.id] = spr

      #create any trainers
      #for trainerNode in root.getChildren("trainer"):
      #   spr = trainer.Trainer(trainerNode, self)
      #   self.sprites[spr.id] = spr

      #create objects
      #self.objects = []
      #for objectNode in root.getChildren("object"):
      #   obj = environment_objects.createObject(objectNode, self)
      #   self.objects.append(obj)
      #self.strengthActive = False
      
      #create script and warp events, adding them to the events dictionary
      #if a load script is defined, create it
      #self.events = {}
      #loadScript = None
      #for s in root.getChildren("script"):
      #   trigger = s.getAttr("trigger", data.D_STRING)
      #   if trigger == "load":
      #      loadScript = script_engine.scriptFromNode(s, self.scriptDefault)   
      #   else:
      #      position = tuple(s.getAttr("position", data.D_INT2LIST)) 
      #      self.events[position] = events.ScriptEvent(s, self)
            
      #for w in root.getChildren("warp"):
      #   position = tuple(w.getAttr("position", data.D_INT2LIST))
      #   self.events[position] = events.Warp(w, self)

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
         raise ValueError
      root = tree.getroot()
      self.size = int(root.attrib["width"]), int(root.attrib["height"])

      #create each layer, separating the collision and behaviour data
      self.layers = []
      for layer in root.findall("layer"):
         l = Layer()
         l.openTMXNode(layer)
         if l.level >= 0: #collision layer indicated by level == -1
            self.layers.append(l)

   @property
   def pixelSize(self):
      return (self.size[0]*self.tileset.tileSize[0],
              self.size[1]*self.tileset.tileSize[1])

   def renderTo(self, canvas):
      canvas.delete("all")
      
      for layer in self.layers:
         for x in range(0, self.size[0]):
            for y in range(0, self.size[1]):
               tileIndex = layer[(x,y)]
               tileLoc = ((x*self.tileset.tileSize[0])+0,
                          (y*self.tileset.tileSize[1])+0)
               canvas.create_image(tileLoc, image=self.tileset[tileIndex], anchor=NW)

      for event in ("npc", "warp", "script", "object"):
         for eventNode in self.root.findall(event):
            if (event == "script") and (eventNode.attrib.get("trigger", "") == "load"):
               continue
            pos = tuple(int(a) for a in eventNode.attrib["position"].split(","))
            tileLoc = (pos[0]*self.tileset.tileSize[0],
                       pos[1]*self.tileset.tileSize[1])
            canvas.create_image(tileLoc, image=self.tiles[event], anchor=NW, tags="event")
            self.events[pos] = eventNode

   def addEvent(self, eventName):
      node = ET.Element(eventName)

      posX = 0
      posY = 0
      while True:
         if self.getObjectAt((posX, posY)) is None:
            break
         posX += 1
         if posX >= self.size[0]:
            posX = 0
            posY += 1

      node.attrib["position"] = "{},{}".format(posX, posY)
      self.root.append(node)
      self.events[(posX, posY)] = node
      
   def getObjectAt(self, position):
      try:
         return self.events[position]
      except KeyError:
         return None

   def moveObject(self, oldPos, newPos):
      obj = self.events[oldPos]
      del self.events[oldPos]
      obj.attrib["position"] = ",".join(map(str, newPos))
      self.events[newPos] = obj     

   def dumpOnto(self, root):
      for k in self.events:
         root.append(self.events[k])
      
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

