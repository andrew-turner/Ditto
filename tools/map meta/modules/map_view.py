from tkinter import *

import modules.tilemap as tilemap
import modules.map_objects_view as map_objects_view
import modules.map_object_pallette as map_object_pallette

class MapView(Frame):
   def __init__(self, master):
      Frame.__init__(self, master)

      self.grid_rowconfigure(0, weight=1)
      self.grid_columnconfigure(0, weight=1)

      self.scrollX = Scrollbar(self, orient=HORIZONTAL)
      self.scrollX.grid(row=1, column=0, sticky=E+W)

      self.scrollY = Scrollbar(self, orient=VERTICAL)
      self.scrollY.grid(row=0, column=1, sticky=N+S)
      
      self.canvas = Canvas(self, bg="red", xscrollcommand=self.scrollX.set, yscrollcommand=self.scrollY.set)
      self.canvas.grid(row=0, column=0, sticky=N+S+E+W)
      self.canvas.tag_bind("event", "<ButtonPress-1>", self.onMouseDown)
      self.canvas.tag_bind("event", "<B1-Motion>", self.onMouseMotion)
      self.canvas.tag_bind("event", "<ButtonRelease-1>", self.onMouseUp)

      self.scrollX.config(command=self.canvas.xview)
      self.scrollY.config(command=self.canvas.yview)

      self.dragData = {"x": 0,
                       "y": 0,
                       "obj": None,
                       "oldPos": (0,0)}

      self.currentShownObject = None

      self.rhFrame = Frame(self)
      self.rhFrame.grid(row=0, column=2)
      
      self.objView = map_objects_view.MapObjectsView(self.rhFrame)
      self.objView.pack(side=TOP, fill=X)

      self.objPallette = map_object_pallette.MapObjectPallette(self.rhFrame)
      self.objPallette.pack(side=TOP, fill=X)
      self.objPallette.bindCreateMethod(self.addEvent)

      self.map = None

   def showData(self, mMap):
      self.map = mMap

      self.canvas.config(scrollregion=(0,0,self.map.pixelSize[0],self.map.pixelSize[1]), width=self.map.pixelSize[0])
      
      self.map.renderTo(self.canvas)

   def dumpOnto(self, root):
      if self.currentShownObject is not None:
         self.objView.dumpOnto(self.currentShownObject)
      self.map.dumpOnto(root)

   def addEvent(self, eventName):
      if self.map is not None:
         self.map.addEvent(eventName)

      self.map.renderTo(self.canvas)

   def onMouseDown(self, e):
      canvCoords = (self.canvas.canvasx(e.x),
                    self.canvas.canvasy(e.y))
      tileLoc = (int(self.canvas.canvasx(e.x)/self.map.tileSize[0]),
                 int(self.canvas.canvasy(e.y)/self.map.tileSize[1]))
      
      obj = self.map.getObjectAt(tileLoc)
      im = self.canvas.find_closest(canvCoords[0], canvCoords[1])[0]

      if obj is not None:
         if self.currentShownObject is not None:
            self.objView.dumpOnto(self.currentShownObject)
         
         self.dragData["x"] = e.x
         self.dragData["y"] = e.y
         self.dragData["obj"] = im
         self.dragData["oldPos"] = tileLoc

         self.objView.showData(obj)
         self.currentShownObject = obj

      else:
         self.dragData["obj"] = None

   def onMouseMotion(self, e):
      deltaX = e.x - self.dragData["x"]
      deltaY = e.y - self.dragData["y"]

      obj = self.dragData["obj"]
      if obj is not None:
         self.canvas.move(self.dragData["obj"], deltaX, deltaY)

      self.dragData["x"] = e.x
      self.dragData["y"] = e.y

   def onMouseUp(self, e):
      canvCoords = (self.canvas.canvasx(e.x),
                    self.canvas.canvasy(e.y))
      tileLoc = (int(self.canvas.canvasx(e.x)/self.map.tileSize[0]),
                 int(self.canvas.canvasy(e.y)/self.map.tileSize[1]))

      obj = self.dragData["obj"]

      if (self.map.getObjectAt(tileLoc) is None) and (obj is not None):
         self.map.moveObject(self.dragData["oldPos"], tileLoc)
         self.objView.showData(self.map.getObjectAt(tileLoc))
      else:
         tileLoc = self.dragData["oldPos"]
         
      if obj is not None:
         reqPos = (tileLoc[0]*self.map.tileSize[0],
                   tileLoc[1]*self.map.tileSize[1])
         self.canvas.coords(self.dragData["obj"], reqPos)
      
      
      self.dragData["x"] = 0
      self.dragData["y"] = 0
      self.dragData["obj"] = None
      
