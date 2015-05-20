import random

import eng.data as data

from eng.constants.stats import *

STAT_NAMES = {}
BATTLE_NAMES = {}
initialised = False

def init():
   global initialised
   
   STAT_NAMES["attack"] = ST_ATTACK
   STAT_NAMES["defense"] = ST_DEFENSE
   STAT_NAMES["speed"] = ST_SPEED
   STAT_NAMES["spatk"] = ST_SPATTACK
   STAT_NAMES["spdef"] = ST_SPDEFENSE
   STAT_NAMES["evasion"] = ST_EVASION
   STAT_NAMES["accuracy"] = ST_ACCURACY

   BATTLE_NAMES[ST_ATTACK] = "Attack"
   BATTLE_NAMES[ST_DEFENSE] = "Defense"
   BATTLE_NAMES[ST_SPEED] = "Speed"
   BATTLE_NAMES[ST_SPATTACK] = "Special Attack"
   BATTLE_NAMES[ST_SPDEFENSE] = "Special Defense"
   BATTLE_NAMES[ST_EVASION] = "Evasion"
   BATTLE_NAMES[ST_ACCURACY] = "Accuracy"

   initialised = True

class MoveEffect():
   def __init__(self, node):
      if not initialised:
         init()
      
      self.chance = node.getOptionalAttr("chance", data.D_INT, None)

   def doEffect(self, user, target, task):
      if not initialised:
         init()
      
      if self.chance is None:
         self.activate(user, target, task)
         
      else:
         if random.random() < self.chance/100.0:
            self.activate(user, target, task)

      
   def activate(self, user, target, task):
      pass

