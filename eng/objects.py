import os

from . import script_engine
from . import settings
from . import data
from . import tileset

class VisibleObject(script_engine.ScriptableObject):
   def __init__(self):
      script_engine.ScriptableObject.__init__(self)
      
      self.map = None #no map yet
      self.position = None #no position yet
      self.level = None #no level yet
      self.switch = False
      self.visible = True #we're visible
      self.tileset = None #no tileset yet
      self.tileOffset = None
      self.animations = {} #initialize animations dictionary
      self.animation = None

   def tick(self):
      if self.animation is not None:
         if self.animation.active: #if currently animated
            self.animation.tick() #advance the animation

   def getTile(self):
      if self.animation is not None:
         if self.animation.active: #if animated
            i = self.animation.currentFrame #get the frame from the animation
         else: #else
            i = 0 #get the first tile
         return self.tileset[i] #return the required tile
      else:
         return self.tileset[0]

   def setPosition(self, mMap, position, level):
      self.map = mMap #store map
      self.position = position #store position
      self.level = level #store level
         

      
                            

