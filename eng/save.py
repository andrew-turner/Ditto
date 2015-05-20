import pickle

from . import script_engine

def readSave(fn):
   #open the file for reading, load the save game, and close
   try:
      with open(fn, "rb") as f:
         return pickle.load(f)
   except IOError:
      raise error.DittoIOException("Save file", fn)

def writeSave(savegame):
   #open the file for writing, dump the save game, and close
   try:
      with open(savegame.fn, "wb") as f:
         pickle.dump(savegame, f)
   except IOError:
      raise error.DittoIOException("Save file", fn)

class Save(script_engine.ScriptableObject):
   """
   Save object to store game save data.

   Gets pickled and unpickled to act as a save.
   """
   
   def __init__(self, fn):
      """
      Create a blank save.

      fn - the filename where it will be saved.
      """
      
      #store fn
      self.fn = fn

      #initialise world position data
      self.currentMap = None
      self.currentPosition = None
      self.currentLevel = None
      self.currentDirection = None

      #initialise player data
      self.party = None
      self.bag = None

      self.playtime = 0

      #initialise script engine save variables
      self.variables = {}
      self.variables["PLAYERNAME"] = "(No name)"
      self.variables["MONEY"] = 0
      self.variables["GENDER"] = "MALE"

   #scripting functions
   def getVar(self, name):
      #return the value if it exists, else raise an error
      try:
         return self.variables[name]
      except KeyError:
         raise script_engine.DLookupError(name)

   def setVar(self, name, val):
      #even if the value isn't yet specified, set it
      self.variables[name] = val

   
