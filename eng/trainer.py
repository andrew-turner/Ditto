import xml.etree.ElementTree as ET

from . import npc
from . import data
from . import script_engine

PREBATTLE = """
lock();
CALLER.exclamation();
waitFrames(20);
CALLER.walkToPlayer();
waitFor(CALLER);
facePlayer();
dialog("%s", 1);
dialog("(battle)", 1);
dialog("%s", 1);
unlock();
"""

POSTBATTLE = """
lock();
facePlayer();
dialog("%s", 1);
unlock();
"""

class Trainer(npc.NPC):

   def __init__(self, node, mMap):
      npc.NPC.__init__(self, node, mMap)

      self.scriptCommands["walkToPlayer"] = self.command_walkToPlayer

      self.distance = node.getAttr("distance", data.D_INT)
      self.stepsToTake = 0

      self.hasBattled = False
      self.scriptEngine = script_engine.ScriptEngine()

      prebattleNode = node.getChild("prebattle")
      defeatNode = node.getChild("defeat")
      postbattleNode = node.getChild("postbattle")

      source = PREBATTLE % (prebattleNode.getAttr("text", data.D_STRING),
                                defeatNode.getAttr("text", data.D_STRING))
      scriptNode = ET.Element("script")
      scriptNode.attrib["trigger"] = "walkonto"
      self.prebattle = script_engine.scriptFromNode(scriptNode)
      self.prebattle.build(source, "Ditto main", "TRAINER")

      source = POSTBATTLE % postbattleNode.getAttr("text", data.D_STRING)
      scriptNode = ET.Element("script")
      scriptNode.attrib["trigger"] = "investigate"
      self.postbattle = script_engine.scriptFromNode(scriptNode)
      self.postbattle.build(source, "Ditto main", "TRAINER")

   def onInvestigate(self):
      if self.hasBattled:
         self.scriptEngine.run(self.postbattle, self)
      else:
         self.stepsToTake = 0
         self.scriptEngine.run(self.prebattle, self)
         self.hasBattled = True
         self.move = npc.MT_NONE

   def checkPosition(self, pos):
      for d in range(1, self.distance+1):
         lookAt = self.getPositionInFront(d)
         if lookAt == pos:
            self.stepsToTake = d-1
            return True
      return False

   def activate(self):
      if not self.hasBattled:
         self.scriptEngine.run(self.prebattle, self)
         self.hasBattled = True
         self.move = npc.MT_NONE

   def command_walkToPlayer(self):
      if self.stepsToTake > 0:
         self.walk(self.direction, True)
         for x in range(1, self.stepsToTake):
            self.stepQueue.append(self.direction)
