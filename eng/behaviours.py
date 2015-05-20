import eng.data as data
import eng.globs as globs
import eng.script_engine as script_engine

from eng.constants.behaviours import *

#behaviours
BEHAVIOURSCRIPTS_INVESTIGATE = {}
BEHAVIOURSCRIPTS_WALKONTO = {}

BUILTINBEHAVIOURS = {}
BUILTINBEHAVIOURNAMES = {"slide": B_SLIDE,
                         "ledgedown": B_LEDGEDOWN,
                         "ledgeleft": B_LEDGELEFT,
                         "ledgeright": B_LEDGERIGHT,
                         "waterfall": B_WATERFALL,
                         "forcedown": B_FORCEDOWN,
                         "forceup": B_FORCEUP,
                         "forceleft": B_FORCELEFT,
                         "forceright": B_FORCERIGHT}

def init():
   behavioursRoot = data.getTreeRoot(globs.BEHAVIOURS)
   for behaviourNode in behavioursRoot.getChildren("behaviour"):
      trigger = behaviourNode.getOptionalAttr("trigger", data.D_STRING)
      
      if trigger is not None:
         s = behaviourNode.getChild("script")
         i = behaviourNode.getAttr("index", data.D_INT)         
         scr = script_engine.scriptFromNode(s)
         if trigger == "investigate":
            BEHAVIOURSCRIPTS_INVESTIGATE[i] = scr
         elif trigger == "walkonto":
            BEHAVIOURSCRIPTS_WALKONTO[i] = scr
         else:
            raise data.DInvalidAttributeError(behaviourNode, trigger)

      else:
         builtinName = behaviourNode.getAttr("builtin", data.D_STRING)
         i = behaviourNode.getAttr("index", data.D_INT)
         try:
            builtin = BUILTINBEHAVIOURNAMES[builtinName]
         except KeyError:
            raise data.DInvalidAttributeError(behaviourNode, "builtin")
         BUILTINBEHAVIOURS[i] = builtin
