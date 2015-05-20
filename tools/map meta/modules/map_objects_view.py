import xml.etree.ElementTree as ET

from tkinter import *

from modules.map_objects_properties import (IdProperty,
                                            TilesetProperty,
                                            PositionProperty,
                                            LevelProperty,
                                            MovementProperty,
                                            RadiusProperty,
                                            CourseProperty,
                                            ScriptIdProperty,
                                            ScriptTriggerProperty,
                                            TargetMapProperty,
                                            TargetPositionProperty,
                                            TriggerProperty,
                                            TypeProperty)

class MapObjectsView(Frame):
   def __init__(self, master):
      Frame.__init__(self, master)

      self.config(relief=RIDGE, bd=2)
      
      self.npcView = NpcObjectView(self)
      self.warpView = WarpObjectView(self)
      self.scriptView = ScriptObjectView(self)
      self.objectView = ObjectObjectView(self)

      self.currentView = self.npcView
      self.currentView.pack(side=TOP)

   def showData(self, node):
      self.currentView.pack_forget()

      if node.tag == "npc":
         self.currentView = self.npcView
      elif node.tag == "warp":
         self.currentView = self.warpView
      elif node.tag == "script":
         self.currentView = self.scriptView
      elif node.tag == "object":
         self.currentView = self.objectView
      else:
         raise ValueError

      self.currentView.pack(side=TOP)
      self.currentView.showData(node)

   def dumpOnto(self, eventNode):
      for k in self.currentView.propertyViews:
         self.currentView.propertyViews[k].dumpOnto(eventNode)         

class NpcObjectView(Frame):   
   def __init__(self, master):
      Frame.__init__(self, master)

      self.propertyViews = {}

      w = IdProperty(self)
      w.pack(side=TOP)
      self.propertyViews["ID"] = w

      w = TilesetProperty(self)
      w.pack(side=TOP)
      self.propertyViews["Tileset"] = w

      w = PositionProperty(self)
      w.pack(side=TOP)
      self.propertyViews["Position"] = w

      w = LevelProperty(self)
      w.pack(side=TOP)
      self.propertyViews["Level"] = w

      w = MovementProperty(self)
      w.pack(side=TOP)
      self.propertyViews["Movement"] = w

      w = RadiusProperty(self)
      w.pack(side=TOP)
      self.propertyViews["Radius"] = w

      w = CourseProperty(self)
      w.pack(side=TOP)
      self.propertyViews["Course"] = w

      w = ScriptIdProperty(self)
      w.pack(side=TOP)
      self.propertyViews["Script ID"] = w

      w = ScriptTriggerProperty(self)
      w.pack(side=TOP)
      self.propertyViews["Script trigger"] = w

   def showData(self, node):
      for k in self.propertyViews:
         self.propertyViews[k].loadData(node)

class WarpObjectView(Frame):
   def __init__(self, master):
      Frame.__init__(self, master)

      self.propertyViews = {}

      w = PositionProperty(self)
      w.pack(side=TOP)
      self.propertyViews["Position"] = w

      w = TargetMapProperty(self)
      w.pack(side=TOP)
      self.propertyViews["Target map"] = w

      w = TargetPositionProperty(self)
      w.pack(side=TOP)
      self.propertyViews["Target position"] = w

   def showData(self, node):
      for k in self.propertyViews:
         self.propertyViews[k].loadData(node)

class ScriptObjectView(Frame):
   def __init__(self, master):
      Frame.__init__(self, master)

      self.propertyViews = {}

      w = PositionProperty(self)
      w.pack(side=TOP)
      self.propertyViews["Position"] = w

      w = IdProperty(self)
      w.pack(side=TOP)
      self.propertyViews["ID"] = w

      w = TriggerProperty(self)
      w.pack(side=TOP)
      self.propertyViews["Trigger"] = w

   def showData(self, node):
      for k in self.propertyViews:
         self.propertyViews[k].loadData(node)

class ObjectObjectView(Frame):
   def __init__(self, master):
      Frame.__init__(self, master)

      self.propertyViews = {}

      w = PositionProperty(self)
      w.pack(side=TOP)
      self.propertyViews["Position"] = w

      w = TypeProperty(self)
      w.pack(side=TOP)
      self.propertyViews["Type"] = w

   def showData(self, node):
      for k in self.propertyViews:
         self.propertyViews[k].loadData(node)
