import xml.etree.ElementTree as ET

from tkinter import *

from modules.map_data_properties import (IdProperty,
                                         MapFileProperty,
                                         TilesetProperty,
                                         MusicProperty,
                                         NameProperty,
                                         ScriptFileProperty,
                                         WeatherProperty,
                                         LoadScriptProperty,
                                         LeftConnectionProperty,
                                         LeftOffsetProperty,
                                         RightConnectionProperty,
                                         RightOffsetProperty,
                                         UpConnectionProperty,
                                         UpOffsetProperty,
                                         DownConnectionProperty,
                                         DownOffsetProperty)

class MapDataView(Frame):
   def __init__(self, master):
      Frame.__init__(self, master)

      self.config(relief=RIDGE, bd=2)

      self.fn = None

      self.propertyViews = {}

      w = IdProperty(self)
      w.pack(side=TOP)
      self.propertyViews["ID"] = w

      w = MapFileProperty(self)
      w.pack(side=TOP)
      self.propertyViews["Map file"] = w

      w = TilesetProperty(self)
      w.pack(side=TOP)
      self.propertyViews["Tileset"] = w

      w = MusicProperty(self)
      w.pack(side=TOP)
      self.propertyViews["Music"] = w

      w = NameProperty(self)
      w.pack(side=TOP)
      self.propertyViews["Name"] = w

      w = ScriptFileProperty(self)
      w.pack(side=TOP)
      self.propertyViews["Script file"] = w

      w = WeatherProperty(self)
      w.pack(side=TOP)
      self.propertyViews["Weather"] = w

      w = LoadScriptProperty(self)
      w.pack(side=TOP)
      self.propertyViews["Load script"] = w

      w = LeftConnectionProperty(self)
      w.pack(side=TOP)
      self.propertyViews["Left connection"] = w

      w = LeftOffsetProperty(self)
      w.pack(side=TOP)
      self.propertyViews["Left offset"] = w

      w = RightConnectionProperty(self)
      w.pack(side=TOP)
      self.propertyViews["Right connection"] = w

      w = RightOffsetProperty(self)
      w.pack(side=TOP)
      self.propertyViews["Right offset"] = w

      w = UpConnectionProperty(self)
      w.pack(side=TOP)
      self.propertyViews["Up connection"] = w

      w = UpOffsetProperty(self)
      w.pack(side=TOP)
      self.propertyViews["Up offset"] = w

      w = DownConnectionProperty(self)
      w.pack(side=TOP)
      self.propertyViews["Down connection"] = w

      w = DownOffsetProperty(self)
      w.pack(side=TOP)
      self.propertyViews["Down offset"] = w

   def showData(self, fn):
      self.fn = fn

      tree = ET.parse(fn)
      root = tree.getroot()
      
      for k in self.propertyViews:
         self.propertyViews[k].val = ""
         self.propertyViews[k].loadData(root)

   def dumpOnto(self, root):
      for k in self.propertyViews:
         self.propertyViews[k].dumpOnto(root)




