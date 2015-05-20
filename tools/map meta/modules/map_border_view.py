import xml.etree.ElementTree as ET

from tkinter import *

from modules.map_border_properties import (NWProperty,
                                           NEProperty,
                                           SWProperty,
                                           SEProperty)

class MapBorderView(Frame):
   def __init__(self, master):
      Frame.__init__(self, master)

      self.config(relief=RIDGE, bd=2)

      self.canvas = Canvas(self, bg="blue", width=32, height=32)
      self.canvas.pack(side=TOP)

      self.frame = Frame(self)
      self.frame.pack(side=TOP)

      self.propertyViews = {}

      w = NWProperty(self.frame)
      w.pack(side=TOP)
      self.propertyViews["NW"] = w
      w.bindChangeCallback(self.onChangeVal)

      w = NEProperty(self.frame)
      w.pack(side=TOP)
      self.propertyViews["NE"] = w
      w.bindChangeCallback(self.onChangeVal)

      w = SWProperty(self.frame)
      w.pack(side=TOP)
      self.propertyViews["SW"] = w
      w.bindChangeCallback(self.onChangeVal)

      w = SEProperty(self.frame)
      w.pack(side=TOP)
      self.propertyViews["SE"] = w
      w.bindChangeCallback(self.onChangeVal)

      self.map = None
      self.root = None

   def onChangeVal(self, *args):
      self.renderBorder()

   def showData(self, fn, mMap):
      self.fn = fn      
      self.map = mMap

      tree = ET.parse(fn)
      self.root = tree.getroot()

      for k in self.propertyViews:
         self.propertyViews[k].loadData(self.root)

      self.renderBorder()

   def renderBorder(self):
      self.canvas.delete("all")
      
      self.canvas.config(width=self.map.tileSize[0]*2,
                         height=self.map.tileSize[1]*2)

      indexes = (self.propertyViews["NW"].val,
                 self.propertyViews["NE"].val,
                 self.propertyViews["SW"].val,
                 self.propertyViews["SE"].val)

      for x in range(0, 2):
         for y in range(0, 2):
            index = indexes[x+(y*2)]
            
            try:
               index = int(index)
            except ValueError:
               continue

            try:
               tile = self.map.tileset[index-1]
            except KeyError:
               continue

            pos = ((x*self.map.tileSize[0])+1,
                   (y*self.map.tileSize[1])+1)
            self.canvas.create_image(pos, image=tile, anchor=NW)

   def dumpOnto(self, root):
      for k in self.propertyViews:
         self.propertyViews[k].dumpOnto(root)

         
            
               

      
         

      
