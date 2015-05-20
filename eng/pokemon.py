import os
import math

import pygame

from . import globs
import random
from . import settings
from . import data
from . import moves
from . import script_engine

from eng.constants.stats import *

STATNAMES = {"hp": ST_HP,
             "attack": ST_ATTACK,
             "defense": ST_DEFENSE,
             "speed": ST_SPEED,
             "spatk": ST_SPATTACK,
             "spdef": ST_SPDEFENSE}

#gender constants
G_MALE = 0
G_FEMALE = 1
G_NONE = 2

#nature directory
NATURES = {}

def expAtLevel(level, growthRate):
   """
   Calculate the experience required to reach a given level for a pokemon on a given growth rate.

   level - the level of the pokemon
   growthRate - the growth rate
   """

   #note float division, then we return the floor integer
   #nothing here to stop the level being greater than 100...
   
   if growthRate == "Fast":
      ans = (4*(level**3))/5.0

   elif growthRate == "Medium": #Medium Fast on Bulbapedia
      ans = level**3

   elif growthRate == "Slow":
      ans = (5*(level**3))/4.0

   elif growthRate == "Parabolic": #Medium Slow on Bulbapedia
      ans = ((6*(level**3))/5.0)-(15*(level**2))+(100*level)-140

   elif growthRate == "Erratic":
      if level <= 50:
         ans = ((level**3)*(100-level))/50.0
      elif level <= 68:
         ans = ((level**3)*(150-level))/100.0
      elif level <= 98:
         ans = ((level**3)*((1911-(10*level))/3.0))/500.0
      else:
         ans = ((level**3)*(160-level))/100.0

   elif growthRate == "Fluctuating":
      if level <= 15:
         ans = (level**3)*((((level+1)/3.0)+24)/50.0)
      elif level <= 36:
         ans = (level**3)*((level+14)/50.0)
      else:
         ans = (level**3)*(((level/2.0)+32)/50.0)

   return int(math.floor(ans))

def init(naturesFn):
   root = data.getTreeRoot(naturesFn)
   for natureNode in root.getChildren("nature"):
      name = natureNode.getAttr("name", data.D_STRING)
      inc = natureNode.getOptionalAttr("increases", data.D_STRING)
      dec = natureNode.getOptionalAttr("decreases", data.D_STRING)
      try:
         if inc is not None:
            inc = STATNAMES[inc]
      except KeyError:
         raise data.DInvalidAttributeError(natureNode, "increases")
      try:
         if dec is not None:
            dec = STATNAMES[dec]
      except KeyError:
         raise data.DInvalidAttributeError(natureNode, "decreases")
      NATURES[natureNode.getAttr("id", data.D_STRING)] = (name, inc, dec)
                                                    
class Pokemon():
   """Class for a single pokemon."""
   
   def __init__(self, species, level):
      self.species = species

      root = data.getTreeRoot(globs.POKEMON, "Pokemon global")

      for sp in root.getChildren("species"):
         if sp.getAttr("id", data.D_STRING) == self.species:
            self.speciesNode = sp
            break                           
      
      self.nickname = None
      
      self.level = level
      growthNode = self.speciesNode.getChild("growth")
      self.growthRate = growthNode.getAttr("rate", data.D_STRING)
      self.exp = expAtLevel(level, self.growthRate)

      typeNode = self.speciesNode.getChild("type")
      self.type1 = typeNode.getAttr("primary", data.D_STRING)
      self.type2 = typeNode.getOptionalAttr("secondary", data.D_STRING, None)

      self.PID = random.randint(0, 4294967295)
      self.trainer = None
      self.trainerID = None

      self.ability = None

      self.gender = G_MALE
      self.nature = random.choice(list(NATURES.keys()))
      self.shiny = False

      self.form = 0
      self.happiness = 0
      self.pokerus = False
      
      self.EVs = {ST_HP: 0,
                  ST_ATTACK: 0,
                  ST_DEFENSE: 0,
                  ST_SPEED: 0,
                  ST_SPATTACK: 0,
                  ST_SPDEFENSE: 0}
      
      self.IVs = {ST_HP: random.randint(0,31),
                  ST_ATTACK: random.randint(0,31),
                  ST_DEFENSE: random.randint(0,31),
                  ST_SPEED: random.randint(0,31),
                  ST_SPATTACK: random.randint(0,31),
                  ST_SPDEFENSE: random.randint(0,31)}

      self.stats = {}
      self.calcStats()

      self.currentHP = random.randint(0, self.stats[ST_HP]) #self.stats[ST_HP]
      self.status = None

      self.moves = [None, None, None, None]
      movesNode = self.speciesNode.getChild("attacks")
      moveNodes = sorted(movesNode.getChildren("move"), key=lambda n: int(n.getAttr("level", data.D_INT)))
      i = 0
      for node in moveNodes[-4:]:
         self.moves[i] = moves.Move(node.getAttr("id", data.D_STRING))
         i += 1
      
      self.ballCaughtIn = random.choice(["MASTER", "POKE", "GREAT", "SAFARI"])

      self.heldItem = None

      ###############
      if species == "ABRA":
         self.moves[1] = moves.Move("FLASH")
      ###############

   def calcStats(self):
      statsNode = self.speciesNode.getChild("basestats")
      
      baseStats = {}
      baseStats[ST_HP] = statsNode.getAttr("hp", data.D_INT)
      baseStats[ST_ATTACK] = statsNode.getAttr("attack", data.D_INT)
      baseStats[ST_DEFENSE] = statsNode.getAttr("defense", data.D_INT)
      baseStats[ST_SPATTACK] = statsNode.getAttr("spatk", data.D_INT)
      baseStats[ST_SPDEFENSE] = statsNode.getAttr("spdef", data.D_INT)
      baseStats[ST_SPEED] = statsNode.getAttr("speed", data.D_INT)

      value = (((self.IVs[ST_HP]+(2*baseStats[ST_HP])+(self.EVs[ST_HP]/4)+100)*self.level)/100)+10
      self.stats[ST_HP] = int(value * self.getNatureMultiplier(ST_HP))

      for stat in [ST_ATTACK, ST_DEFENSE, ST_SPATTACK, ST_SPDEFENSE, ST_SPEED]:
         value = (((self.IVs[stat]+(2*baseStats[stat])+(self.EVs[stat]/4))*self.level)/100)+5
         self.stats[stat] = int(value * self.getNatureMultiplier(stat))

   def getNatureMultiplier(self, stat):
      name, inc, dec = NATURES[self.nature]
      if stat == inc:
         return 1.1
      elif stat == dec:
         return 0.9
      else:
         return 1

   def getName(self):
      if self.nickname is None:
         return self.speciesNode.getAttr("name", data.D_STRING)
      else:
         return self.nickname

   def getNatureName(self):
      return NATURES[self.nature][0]

   def getBattler(self):
      graphicsNode = self.speciesNode.getChild("graphics")
      battleNode = graphicsNode.getChild("battle")
      battler = data.getImage(battleNode.getAttr("front", data.D_FILENAME), battleNode.ditto_fn)
      trans = battleNode.getAttr("transparency", data.D_INT3LIST)
      trans = (250,0,250)
      battler.set_colorkey(trans)

      return battler

   def getBackBattler(self):
      graphicsNode = self.speciesNode.getChild("graphics")
      battleNode = graphicsNode.getChild("battle")
      fn = battleNode.getAttr("front", data.D_FILENAME)
      root, ext = os.path.splitext(fn)
      fn = root + "b" + ext
      battler = data.getImage(fn, battleNode.ditto_fn)
      trans = battleNode.getAttr("transparency", data.D_INT3LIST)
      trans = (250,0,250)
      battler.set_colorkey(trans)

      return battler

   def getExpToNext(self):
      if self.level >= 100:
         return 0
      else:
         growthNode = self.speciesNode.getChild("growth")
         growthRate = growthNode.getAttr("rate", data.D_STRING)
         return expAtLevel(self.level+1, growthRate) - self.exp

   def getBaseExp(self):
      defeatNode = self.speciesNode.getChild("defeat")
      return defeatNode.getAttr("exp", data.D_INT)
      
class Party(script_engine.ScriptableObject):
   def __init__(self):
      script_engine.ScriptableObject.__init__(self)
      
      #self.scriptCommands["add"] = self.command_add
      #self.scriptCommands["hasMove"] = self.command_hasMove
      #self.scriptCommands["healAll"] = self.command_healAll
      
      self.pokemon = []

   def add(self, poke):
      if len(self.pokemon) < 6:
         self.pokemon.append(poke)

   def switch(self, i1, i2):
      self.pokemon[i1], self.pokemon[i2] = self.pokemon[i2], self.pokemon[i1]

   def command_hasMove(self, move):
      return True

   def command_healAll(self):
      for poke in self.pokemon:
         poke.status = None
         poke.currentHP = poke.stats[0]

   def command_add(self, poke):
      self.add(poke)

   def __getitem__(self, i):
      return self.pokemon[i]

   def __len__(self):
      return len(self.pokemon)
