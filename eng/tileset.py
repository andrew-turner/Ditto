import os
import xml.etree.ElementTree as ET

import pygame

from . import settings
from . import animation
from . import error
from . import globs
from . import data
import eng.resource_ids as resource_ids

class Tileset():
   """Class representing a tileset from a tileset image"""
   
   def __init__(self, tsId):
      """
      Open the tileset image, and set up animations.

      tsId - the tileset's id.
      """

      #parse the XML file
      fn = resource_ids.getTilesetFn(tsId)
      root = data.getTreeRoot(fn)      
      self.tileSize = root.getAttr("tilesize", data.D_INT2LIST) 
      self.transparency = root.getAttr("transparency", data.D_INT3LIST)

      #create the tiles
      tilesetPath = os.path.join(settings.path, "data", root.getAttr("file", data.D_STRING))
      self.openImage(tilesetPath)

      #create animations for the tileset
      self.autoAnimations = {}
      self.walkontoAnimations = {}
      self.scriptAnimations = {}
      for anim in root.getChildren("animation"):
         name = anim.getOptionalAttr("name", data.D_STRING, None)
         trigger = anim.getAttr("trigger", data.D_STRING)
         tile = anim.getAttr("tile", data.D_INT)
         frames = anim.getAttr("frames", data.D_INTLIST)
         a = animation.Animation(frames)
         
         if trigger == "auto":
            a.play(True)
            self.autoAnimations[tile] = a
         elif trigger == "walkonto":
            self.walkontoAnimations[tile] = a
         elif trigger == "script":
            if name is None:
               raise data.DInvalidAttributeError(anim, "trigger")
            self.scriptAnimations[name] = a

   def openImage(self, fn):
      """
      Open the tileset image and cut into tiles.

      fn - the path to the tileset image.
      """

      #get the image, and make sure it's pixel dimensions are consistent
      #tilesets have 1 spacing between each tile,
      #so adding 1 should give a multiple of the tilesize+1
      tilesetImage = data.getImage(fn)
      tilesetImage.set_colorkey(self.transparency)
      
      data.check(((tilesetImage.get_width()+1)%(self.tileSize[0]+1))==0, fn)
      data.check(((tilesetImage.get_height()+1)%(self.tileSize[1]+1))==0, fn)
      dimensions = (int((tilesetImage.get_width()+1)//(self.tileSize[0]+1)),
                    int((tilesetImage.get_height()+1)//(self.tileSize[1]+1)))

      #iterate over each tile, cutting it out and adding to our list
      #go across each row in turn to get index numbering correct
      self.tiles = []
      for y in range(0, dimensions[1]):
         for x in range(0, dimensions[0]):
            tile = tilesetImage.subsurface((x*(self.tileSize[0]+1), y*(self.tileSize[1]+1), self.tileSize[0], self.tileSize[1]))
            self.tiles.append(tile)

      #calculate offset
      self.tileOffset = ((globs.TILESIZE[0]-self.tileSize[0])/2,
                          globs.TILESIZE[1]-self.tileSize[1])

   def tick(self):
      """Update the tileset one frame"""

      #tick each auto animation
      for key in self.autoAnimations:
         self.autoAnimations[key].tick()

   def __getitem__(self, i):
      """Get a tile by index, checking for auto animations"""

      #if the tile has an auto animation, get the tile from that
      #otherwise just take the tile from our list
      if i in self.autoAnimations:
         frame = self.autoAnimations[i].currentFrame
         return self.tiles[frame]
      else:
         return self.tiles[i] #get the required tile

