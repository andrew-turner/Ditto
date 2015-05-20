from tkinter import *

class PropertyView(Frame):

   LABELWIDTH = 15
   ENTRYWIDTH = 30
   
   def __init__(self, master, name):
      Frame.__init__(self, master)

      self.name = name

      l = Label(self, text=name, width=self.LABELWIDTH)
      l.pack(side=LEFT)

      self.var = StringVar()
      
      self.entry = Entry(self, width=self.ENTRYWIDTH, textvariable=self.var)
      self.entry.pack(side=RIGHT)

   @property
   def val(self):
      return self.entry.get()

   @val.setter
   def val(self, val):
      self.entry.delete(0, END)
      self.entry.insert(0, val)

   def bindChangeCallback(self, func):
      self.var.trace("w", func)          

   def loadData(self, root):
      raise NotImplementedError

   def isValid(self):
      raise NotImplementedError

   def dumpOnto(self, root):
      raise NotImplementedError


