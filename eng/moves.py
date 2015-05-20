import os
import random

from . import globs
from . import data
from . import error
from . import settings
from . import ptype
from . import move_effects

from eng.constants.stats import *

C_PHYSICAL = 0
C_SPECIAL = 1
C_STATUS = 2

CATEGORY_NAMES = {"physical": C_PHYSICAL,
                  "special": C_SPECIAL,
                  "status": C_STATUS}

class Move():
   def __init__(self, moveId):
      self.moveId = moveId
      
      root = data.getTreeRoot(globs.MOVES)

      moveNode = None
      for m in root.getChildren("move"):
         if m.getAttr("id", data.D_STRING) == moveId:
            moveNode = m
            break
      if moveNode is None:
         raise error.DittoInvalidResourceException(fn, "MOVE %s" % self.moveId)

      self.name = moveNode.getAttr("name", data.D_STRING)
      
      self.maxPP = moveNode.getAttr("pp", data.D_INT)
      self.currPP = self.maxPP

      self.power = moveNode.getAttr("power", data.D_INT)
      self.category = CATEGORY_NAMES[moveNode.getAttr("category", data.D_STRING)]
      self.type = moveNode.getAttr("type", data.D_STRING)
      self.accuracy = moveNode.getAttr("accuracy", data.D_INT)
      self.priority = 0
      self.critical = 0

      self.effects = []
      for node in moveNode.getChildren():
         self.effects.append(move_effects.getEffect(node))

   def use(self, user, target, task):
      #is the move a critical hit
      isCritical = (random.random() < user.getCriticalChance(self))

      #does it hit or miss
      #accuracy of 0 means always hits
      if self.accuracy == 0:
         isHit = True
      else:
         p = (self.accuracy/100.0) * (user.getAccuracy() / target.getEvasion())
         isHit = (random.random() < p)

      if not isHit:
         task.addMessage("The attack missed!", 40)
         return

      noDamage = False
      if self.power == 0:
         noDamage = True
      else:
         effectiveness = ptype.getEffectiveness(self.type, target.type1)
         if target.type2 is not None:
            effectiveness = ptype.getEffectiveness(self.type, target.type2)
            
         if 0.95 < effectiveness < 1.05:
            pass #tell task nothing
         elif effectiveness > 1.05:         
            task.addMessage("It's super effective!", 30)
         elif effectiveness > 0.05:
            task.addMessage("It's not very effective!", 30)
         else:
            task.addMessage("It had no effect!", 30)
            noDamage = True
            
         d = self.calcDamage(user, target, effectiveness, isCritical)

      if not noDamage:
         target.damage(d)

      for effect in self.effects:
         effect.doEffect(user, target, task)
      

   def calcDamage(self, user, target, typeEffectiveness, isCritical):
      #From Smogon, B/W damage calc
      
      #stats
      if self.category == C_PHYSICAL:
         offensiveStat = user.getEffectiveStat(ST_ATTACK)
         defensiveStat = target.getEffectiveStat(ST_DEFENSE)
      elif self.category == C_SPECIAL:
         offensiveStat = user.getEffectiveStat(ST_SPATTACK)
         defensiveStat = target.getEffectiveStat(ST_SPDEFENSE)
      else: #status
         return 0

      print("Base power: %i" % self.power)

      #base damage
      damage = (((((2*user.level)/5.0)+2)*self.power*(float(offensiveStat)/defensiveStat))/50.0)+2
      print("Base damage: %f" % damage)

      #multi-target

      #critical hit
      if isCritical:
         damage *= 2

      #random
      damage *= random.uniform(0.85, 1)
      print("After random: %f" % damage)

      #STAB
      if self.type == user.type1 or self.type == user.type2:
         damage *= 1.5
      print("After STAB: %f" % damage)

      #type-effectiveness      
      damage *= typeEffectiveness
      print("After type-effectiveness: %f" % damage)

      #burn

      #at least 1
      if damage < 1.0:
         damage = 1

      #final
      return int(damage)
