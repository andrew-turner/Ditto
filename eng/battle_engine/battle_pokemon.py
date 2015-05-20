from . import stat_modifier

from eng.constants.stats import *

CRITICAL_CHANCES = {0: 0.0625,
                    1: 0.125,
                    2: 0.25,
                    3: 0.333,
                    4: 0.5}

class BattlePokemon():
   def __init__(self, poke):
      self.poke = poke

      self.frontBattler = None
      self.backBattler = None

      self.name = poke.getName()
      self.level = poke.level
      self.type1 = poke.type1
      self.type2 = poke.type2
      self.stats = poke.stats
      self.currentHP = poke.currentHP

      self.modifiers = stat_modifier.StatModifier()
      self.critical = 0

      self.moves = poke.moves

      self.baseExp = poke.getBaseExp()

      self.fainted = False

   def getEffectiveStat(self, stat):
      return int(self.stats[stat] * self.modifiers.getMod(stat))

   def getAccuracy(self):
      return self.modifiers.getMod(ST_ACCURACY)

   def getEvasion(self):
      return self.modifiers.getMod(ST_EVASION)

   def getCriticalChance(self, move):
      stage = self.critical + move.critical
      stage = max(0, min(stage, 4))
      return CRITICAL_CHANCES[stage]

   def getFrontBattler(self):
      if self.frontBattler is None:
         self.frontBattler = self.poke.getBattler()

      return self.frontBattler

   def getBackBattler(self):
      if self.backBattler is None:
         self.backBattler = self.poke.getBackBattler()

      return self.backBattler

   def damage(self, amount):
      print("Damage: %i" % amount)
      self.currentHP -= amount
      if self.currentHP < 0:
         self.currentHP = 0
         self.fainted = True
