import os
import re
import xml.etree.ElementTree as ET

from . import objects
from . import script_engine
from . import settings
from . import data

from eng.constants.events import *

class ScriptEvent():
   """Class to allow placing a script onto a map."""
   
   def __init__(self, node, mMap):
      """
      Set up the event and create the script.

      node - the <script> node to get data from.
      mMap - the map the script belongs to.
      """

      #store the map for later
      self.map = mMap

      #parse the node
      self.position = tuple(node.getAttr("position", data.D_INT2LIST))
      trigger = node.getAttr("trigger", data.D_STRING)
      if trigger == "investigate":
         self.trigger = EV_INVESTIGATE
      elif trigger == "walkonto":
         self.trigger = EV_WALKONTO

      #event levels aren't currently checked
      self.level = 0

      #create the script object
      self.script = script_engine.scriptFromNode(node, mMap.scriptDefault)

   def activate(self):
      """Activate the script event."""

      #call the script engine to run the script
      self.map.scriptEngine.run(self.script)

class Warp():
   """
   Class to place warps onto the map.

   Note - possible to do this longhand with a <script> object.
   """
   
   def __init__(self, node, mMap):
      """
      Set up the warp and create the script.

      node - the <warp> node to get data from.
      mMap - the map the warp belongs to.
      """

      #store the map for later
      self.map = mMap

      #get the script engine
      self.scriptEngine = script_engine.ScriptEngine()

      #parse the node
      #target map and position left as strings since they'll be parsed by the script engine
      position = tuple(node.getAttr("position", data.D_INT2LIST))
      targetMap = node.getAttr("targetmap", data.D_STRING)
      targetPosition = node.getAttr("targetposition", data.D_STRING)

      #triggered by walkonto
      self.trigger = EV_WALKONTO

      #event levels aren't currently checked
      self.level = 0
      self.targetLevel = 0

      #create the child script
      #first create the source to execute
      source = """
lock();
waitFrames(4);
fadeOutAndIn(8);
PLAYER.warp(\"%s\", \"%s\");
unlock();
""" % (targetMap, targetPosition)

      #create the script
      self.script = script_engine.scriptFromText(source, "Ditto warp script", "Warp", EV_WALKONTO)
      

   def activate(self):
      """Activate the warp event"""

      #tell the script engine to run the script
      self.scriptEngine.run(self.script, self.map)
