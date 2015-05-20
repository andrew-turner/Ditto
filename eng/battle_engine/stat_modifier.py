from eng.constants.stats import *

MAIN_FRACTIONS = {-6: 0.25,
                  -5: 2.0/7,
                  -4: 1.0/3,
                  -3: 0.4,
                  -2: 0.5,
                  -1: 2.0/3,
                  0: 1.0,
                  1: 1.5,
                  2: 2.0,
                  3: 2.5,
                  4: 3.0,
                  5: 3.5,
                  6: 4.0}

PSEUDO_FRACTIONS = {-6: 1.0/3,
                    -5: 0.375,
                    -4: 3.0/7,
                    -3: 0.5,
                    -2: 0.6,
                    -1: 0.75,
                    0: 1.0,
                    1: 4.0/3,
                    2: 5.0/3,
                    3: 2.0,
                    4: 7.0/3,
                    5: 8.0/3,
                    6: 3.0}

class StatModifier():
   def __init__(self):
      self.levels = {ST_HP: 0,
                     ST_ATTACK: 0,
                     ST_DEFENSE: 0,
                     ST_SPEED: 0,
                     ST_SPATTACK: 0,
                     ST_SPDEFENSE: 0,
                     ST_EVASION: 0,
                     ST_ACCURACY: 0}

   def decrease(self, stat, amount=1):
      if self.levels[stat] == -6:
         return False
      else:
         self.levels[stat] -= amount
         if self.levels[stat] < -6:
            self.levels[stat] = -6
         return True

   def increase(self, stat, amount=1):
      self.levels[stat] = self.levels[stat]
      if self.levels[stat] == 6:
         return False
      else:
         self.levels[stat] += amount
         if self.levels[stat] > 6:
            self.levels[stat] = 6
         return True

   def getMod(self, stat):
      m = self.levels[stat]
      if stat in (ST_EVASION, ST_ACCURACY):
         return PSEUDO_FRACTIONS[self.levels[stat]]
      else:
         return MAIN_FRACTIONS[self.levels[stat]]
