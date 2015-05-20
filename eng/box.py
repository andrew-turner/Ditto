import os

import pygame

import eng.globs as globs
import eng.settings as settings
import eng.data as data

class Box(pygame.Surface):
   """
   Class to provide sized boxes.

   Box(size, fn=None)

   cursor
   sidecursor   
   """
   
   def __init__(self, size, fn=None):
      """
      Draw the box and load cursors if provided.

      size - the size of the box.
      fn - the path to a box xml config file.
      """

      #initialize the pygame Surface
      super().__init__(size)

      #if no filename given, use the game default box
      if fn == None:
         fn = globs.BOX
      self.fn = fn

      #parse the box xml file
      root = data.getTreeRoot(fn)
      tilesetPath = root.getAttr("file", data.D_FILENAME)
      tileset = data.getImage(tilesetPath)
      transparency = root.getAttr("transparency", data.D_INT3LIST)
      tileset.set_colorkey(transparency)
      tileSize = root.getAttr("tilesize", data.D_INT2LIST)
      data.check((tileSize[0]+1)*3==tileset.get_width()+1, tilesetPath)
      data.check((tileSize[1]+1)*3==tileset.get_height()+1, tilesetPath)

      #fill transparent
      self.fill((255,0,255))
      self.set_colorkey((255,0,255))

      #cut each of the nine tiles out from the tileset
      tileNW = tileset.subsurface((0,0), tileSize)
      tileN = tileset.subsurface((tileSize[0]+1,0), tileSize)
      tileNE = tileset.subsurface(((tileSize[0]+1)*2,0), tileSize)
      tileW = tileset.subsurface((0,tileSize[1]+1), tileSize)
      tileC = tileset.subsurface((tileSize[0]+1,tileSize[1]+1), tileSize)
      tileE = tileset.subsurface(((tileSize[0]+1)*2,tileSize[1]+1), tileSize)
      tileSW = tileset.subsurface((0,(tileSize[1]+1)*2), tileSize)
      tileS = tileset.subsurface((tileSize[0]+1,(tileSize[1]+1)*2), tileSize)
      tileSE = tileset.subsurface(((tileSize[0]+1)*2,(tileSize[1]+1)*2), tileSize)

      #calculate how much of the box is not covered by edge tiles - all this middle must be covered by the centre tile
      #work out how many tiles it will take to cover that, and where to start drawing from
      middleSize = size[0]-(2*tileSize[0]), size[1]-(2*tileSize[1])
      dimensions = int((middleSize[0]//tileSize[0])+1), int((middleSize[1]//tileSize[1])+1)
      origin = (size[0]-(dimensions[0]*tileSize[0]))//2, (size[1]-(dimensions[1]*tileSize[1]))//2

      #iterate over the required dimensions, drawing in the centre tiles
      #as we go down the first column only, draw in the left and right side tiles on the edge of the box
      #after we finish each column, draw the top and bottom tiles on the edge
      for x in range(0, dimensions[0]):
         for y in range(0, dimensions[1]):
            self.blit(tileC, (origin[0]+(x*tileSize[0]), origin[1]+(y*tileSize[1])))
            if x == 0:
               self.blit(tileW, (0, origin[1]+(y*tileSize[1])))
               self.blit(tileE, (size[0]-tileSize[0], origin[1]+(y*tileSize[1])))
         self.blit(tileN, (origin[0]+(x*tileSize[0]), 0))
         self.blit(tileS, (origin[0]+(x*tileSize[0]), size[1]-tileSize[1]))

      #draw the corner tiles in the corners
      self.blit(tileNW, (0, 0))
      self.blit(tileNE, (size[0]-tileSize[0], 0))
      self.blit(tileSW, (0, size[1]-tileSize[1]))
      self.blit(tileSE, (size[0]-tileSize[0], size[1]-tileSize[1]))

      #load cursor if provided
      cursorNode = root.getOptionalChild("cursor")
      if cursorNode is not None:
         fn = cursorNode.getAttr("file", data.D_FILENAME)
         self.cursor = data.getImage(fn, root.ditto_fn)
         self.cursor.set_colorkey(transparency)
      else:
         self.cursor = None

      #load side cursor if provided
      sidecursorNode = root.getOptionalChild("sidecursor")
      if sidecursorNode is not None:
         fn = sidecursorNode.getAttr("file", data.D_FILENAME)
         self.sideCursor = data.getImage(fn, root.ditto_fn)
         self.sideCursor.set_colorkey(transparency)
      else:
         self.sideCursor = None

      #borders
      self.xBorder = root.getOptionalAttr("xborder", data.D_INT)
      self.yBorder = root.getOptionalAttr("yborder", data.D_INT)

   def resized(self, size):
      return Box(size, self.fn)
      
