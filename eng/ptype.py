import os

from . import globs
from . import data
from . import settings

initialised = False
types = {}

def init():
   typesRoot = data.getTreeRoot(os.path.join(settings.path, "data", globs.TYPES), "Global Types")
   for typeNode in typesRoot.getChildren("type"):
      types[typeNode.getAttr("id", data.D_STRING)] = pType(typeNode)

   initialised = True

class pType():
   def __init__(self, typeNode):
      self.id = typeNode.getAttr("id", data.D_STRING)
      
      self.doubles = []
      for doubleNode in typeNode.getChildren("double"):
         self.doubles.append(doubleNode.getAttr("against", data.D_STRING))

      self.halves = []
      for halfNode in typeNode.getChildren("half"):
         self.halves.append(halfNode.getAttr("against", data.D_STRING))

      self.zeroes = []
      for zeroNode in typeNode.getChildren("zero"):
         self.zeroes.append(zeroNode.getAttr("against", data.D_STRING))

   def getEffectivenessAgainst(self, typeId):
      if typeId in self.doubles:
         return 2
      elif typeId in self.halves:
         return 0.5
      elif typeId in self.zeroes:
         return 0
      else:
         return 1
      

def getEffectiveness(offensive, defensive):
   if not initialised:
      init()
      
   return types[offensive].getEffectivenessAgainst(defensive)

   
