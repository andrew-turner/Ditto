#! python3

import sys
import traceback
import os
import xml.etree.ElementTree as ET

from tkinter import *
import tkinter.filedialog

from modules.map_data_view import MapDataView
from modules.map_border_view import MapBorderView
from modules.map_view import MapView
from modules.utils import getGameDir
from modules.tilemap import Tilemap

class App():
   def __init__(self, master):
      self.master = master

      self.fn = None
      self.gameDir = None

      self.master.wm_title("Ditto map editor")

      self.menu = Menu(self.master)
      self.master.config(menu=self.menu)

      filemenu = Menu(self.menu)
      self.menu.add_cascade(label="File", menu=filemenu)
      filemenu.add_command(label="New", command=self.callback, accelerator="Ctrl+N")
      filemenu.add_command(label="Open", command=self.menu_open, accelerator="Ctrl+O")
      filemenu.add_command(label="Save", command=self.menu_save, accelerator="Ctrl+S")
      filemenu.add_command(label="Save As", command=self.menu_saveas)

      self.lhFrame = Frame(self.master)
      self.lhFrame.pack(side=LEFT)

      self.mapDataView = MapDataView(self.lhFrame)
      self.mapDataView.pack(side=TOP, fill=X)

      self.mapBorderView = MapBorderView(self.lhFrame)
      self.mapBorderView.pack(side=TOP, fill=X)

      self.mapView = MapView(self.master)
      self.mapView.pack(side=RIGHT, fill=BOTH, expand=1)

      self.master.bind_all("<Control-o>", self.menu_open)
      self.master.bind_all("<Control-s>", self.menu_save)
      
   def menu_open(self, *args):
      self.fn = tkinter.filedialog.askopenfilename(initialdir=".", filetypes=(("XML files", ".xml"),))
      if self.fn != "":
         self.master.wm_title("Ditto map editor: {}".format(os.path.split(self.fn)[1]))
         self.gameDir = getGameDir(self.fn)
         if not self.gameDir:
            raise ValueError
         self.map = Tilemap(self.fn)
         self.mapDataView.showData(self.fn)
         self.mapBorderView.showData(self.fn, self.map)
         self.mapView.showData(self.map)

   def menu_save(self, *args):
      root = ET.Element("map")

      self.mapDataView.dumpOnto(root)
      self.mapBorderView.dumpOnto(root)
      self.mapView.dumpOnto(root)

      tree = ET.ElementTree(root)
      tree.write(self.fn)

   def menu_saveas(self, *args):
      saveFn = tkinter.filedialog.asksaveasfilename(initialdir=".", filetypes=(("XML files", ".xml"),), defaultextension=".xml")

      if saveFn != "":
         self.fn = saveFn
         self.master.wm_title("Ditto map editor: {}".format(os.path.split(self.fn)[1]))
         
         root = ET.Element("map")
         self.mapDataView.dumpOnto(root)
         self.mapBorderView.dumpOnto(root)
         self.mapView.dumpOnto(root)

         tree = ET.ElementTree(root)
         tree.write(saveFn)

   def callback(self, *args):
      print("Callback")

if __name__ == "__main__":
   try:
      root = Tk()
      myApp = App(root)
      root.mainloop()
      
   except Exception:
      print("Python exception generated!")
      print("-"*20)
      traceback.print_exc(file=sys.stdout)
      print("-"*20)
      input()
