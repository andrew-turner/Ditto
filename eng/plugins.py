import os
import imp

from . import settings

"""
Plugin module.

Allows classes to be registered to override the standard classes used in the engine.
Requires that the class' __new__() method checks for plugins. See camera.py.

Game devs then just create a class, which must (I think...) subclass the original, adding whatever functionality they want.
They must register the plugin with a call to overrideClass().
"""

#dict to hold the override classes
CLASSES = {} #{oldClassName: newClass}

def loadAll():
   """
   Load all plugins from the game.

   Must be called before creating any game objects.
   """

   #iterate through each file in the plugins folder
   #if it's a .py file, load the module
   folder = os.path.join(settings.path, "plugins")
   for f in os.listdir(folder):
      name, ext = os.path.splitext(f)
      if ext == ".py":
         fn = os.path.join(folder, f)

         imp.load_source(name, fn)

def overrideClass(old, new):
   """
   Override a class with a new plugin subclass.

   Called from plugin modules to register the plugin.

   old - the class to be overridden.
   new - the subclass to overwrite it with.
   """

   #use the name of the class to store it in the dict
   CLASSES[old.__name__] = new

def checkOverrides(cls):
   """
   Return the class which should be used when a class is instantiated.

   cls - the class which was requested to be instantiated.
   """

   #if we have an override, return it
   #else just use the normal class
   try:
      return CLASSES[cls.__name__]
   except KeyError:
      return cls
