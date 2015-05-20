import os

import eng.data as data
import eng.settings as settings

#interfaces
I_PARTY = 0
I_SUMMARY = 1
I_BAG = 2
I_TRAINERCARD = 3

I_MAP = 10

I_TEXTINPUT = 15

#names
interfaceNames = {"party": I_PARTY,
                  "summary": I_SUMMARY,
                  "bag": I_BAG,
                  "trainercard": I_TRAINERCARD,
                  "map": I_MAP,
                  "textinput": I_TEXTINPUT}

#dict to store filenames
filenames = {}

#default box
BOXPATH = None

def init(fn):
   root = data.getTreeRoot(fn, "Menu config.")

   global BOXPATH
   boxNode = root.getChild("box")
   BOXPATH = os.path.join(settings.path, "data", boxNode.getAttr("file", data.D_STRING))
   
   for interfaceNode in root.getChildren("interface"):
      name = interfaceNode.getAttr("name", data.D_STRING)
      try:
         i = interfaceNames[name]
      except KeyError:
         #raise error
         raise KeyError

      filenames[i] = os.path.join(settings.path, "data", interfaceNode.getAttr("file", data.D_STRING))

def getFilename(i):
   try:
      return filenames[i]
   except KeyError:
      #raise error
      raise KeyError
   
