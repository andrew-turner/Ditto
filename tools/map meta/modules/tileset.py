import os
import xml.etree.ElementTree as ET

from PIL import Image
from PIL import ImageTk

from modules.utils import getGameDir, convertTransparency

class Tileset():
   """Class representing a tileset from a tileset image"""
   
   def __init__(self, tsId, gameDir):
      """
      Open the tileset image, and set up animations.

      tsId - the tileset's id.
      """

      #find the tileset file
      #first, we need the resources config file.
      resourcesFn = os.path.join(gameDir, "data", "resources.xml")
      tree = ET.parse(resourcesFn)
      root = tree.getroot()
      tilesetsNode = root.find("tilesets")
      for tilesetNode in tilesetsNode.findall("tileset"):
         if tilesetNode.attrib["id"] == tsId:
            self.xmlFn = os.path.join(gameDir, "data", tilesetNode.attrib["file"])
            break
      else:
         raise ValueError

      #parse the XML file
      tree = ET.parse(self.xmlFn)
      root = tree.getroot()      
      self.tileSize = [int(a) for a in root.attrib["tilesize"].split(",")]
      self.transparency = [int(a) for a in root.attrib["transparency"].split(",")]

      #create the tiles
      self.imageFn = os.path.join(gameDir, "data", root.attrib["file"])
      self.openImage(self.imageFn)

   def openImage(self, fn):
      """
      Open the tileset image and cut into tiles.

      fn - the path to the tileset image.
      """

      #get the image, and make sure it's pixel dimensions are consistent
      #tilesets have 1 spacing between each tile,
      #so adding 1 should give a multiple of the tilesize+1
      im = Image.open(fn)
      self.tilesetImage = convertTransparency(im, self.transparency)
      
      dimensions = (int((self.tilesetImage.size[0]+1)//(self.tileSize[0]+1)),
                    int((self.tilesetImage.size[1]+1)//(self.tileSize[1]+1)))

      #iterate over each tile, cutting it out and adding to our list
      #go across each row in turn to get index numbering correct
      self.tiles = []
      for y in range(0, dimensions[1]):
         for x in range(0, dimensions[0]):
            left, upper = (x*(self.tileSize[0]+1),
                           y*(self.tileSize[1]+1))
            tile = self.tilesetImage.crop((left,
                                      upper,
                                      left+self.tileSize[0],
                                      upper+self.tileSize[1]))
            self.tiles.append(ImageTk.PhotoImage(tile))

   def __getitem__(self, i):
      """Get a tile by index, checking for auto animations"""

      #if the tile has an auto animation, get the tile from that
      #otherwise just take the tile from our list
      return self.tiles[i] #get the required tile

