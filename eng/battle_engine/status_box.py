import os

import pygame

import eng.data
import eng.settings
import eng.font

from eng.constants.stats import *

HPBAR_HIGH = 0
HPBAR_MIDDLE = 1
HPBAR_LOW = 2
HPBAR_VOID = 3

HPBAR_LOCATION = 15, 2
HPBAR_SIZE = 48, 3
HPBAR_COLOURS = {HPBAR_HIGH: ((112, 248, 168),
                              (88, 208, 128)),
                 HPBAR_MIDDLE: ((248, 224, 56),
                                (200,168,8)),
                 HPBAR_LOW: ((248, 88, 56),
                             (168, 64, 72)),
                 HPBAR_VOID: ((80, 104, 88),
                              (72, 64, 88))}
HPBAR_SPEED = 2

HPBAR_PLAYER_LOCATION = (29,15)

class StatusBox():
   def __init__(self, screen, battleNode, poke):
      self.screen = screen
      self.poke = poke

      self.location = (0,0)
      
      self.hpBar = HpBar(self.screen, battleNode, poke.stats[ST_HP])
      self.hpBar.setValue(poke.currentHP)

      self.changingHP = False
      self.targetHP = 0

   def setLocation(self, location, relative=(0,0)):
      self.location = location[0]+relative[0], location[1]+relative[1]

   def changeHP(self, smooth=True):
      if smooth:
         self.changingHP = True
      else:
         self.hpBar.setValue(self.poke.currentHP)

   def draw(self):
      self.screen.blit(self.back, self.location)
      self.hpBar.draw()

   def tick(self):
      if self.changingHP:
         new = self.hpBar.value-HPBAR_SPEED
         if new < self.poke.currentHP:
            new = self.poke.currentHP
            self.changingHP = False
         self.hpBar.setValue(new)         

class PlayerStatusBox(StatusBox):
   LEFT_SPACER = 16
   RIGHT_SPACER = 9

   LV_1 = 5
   LV_2 = 15
   LV_3 = 23
   
   def __init__(self, screen, battleNode, poke):
      StatusBox.__init__(self, screen, battleNode, poke)
      
      playerpokemonNode = battleNode.getChild("playerpokemon")

      transparency = battleNode.getAttr("transparency", data.D_INT3LIST)

      fn = os.path.join(settings.path, "data", playerpokemonNode.getAttr("file", data.D_STRING))
      self.back = data.getImage(fn, battleNode.ditto_fn)
      self.back.set_colorkey(transparency)

      self.width = self.back.get_width()
      self.height = self.back.get_height()
      
      self.font = font.Font(os.path.join(settings.path, "data", battleNode.getAttr("statusfont", data.D_STRING)))

      self.font.writeText(poke.name, self.back, (self.LEFT_SPACER, self.LV_1))

      text = "Lv%i" % poke.level
      self.font.writeText(text, self.back, (self.width-self.font.calcWidth(text)-self.RIGHT_SPACER, self.LV_1))

   def setLocation(self, location, relative=(0,0)):
      StatusBox.setLocation(self, location, relative)

      self.hpBar.setLocation((self.width-self.hpBar.width-self.RIGHT_SPACER, self.LV_2), self.location)
      self.hpTextLocation = self.location[0]+self.width-self.RIGHT_SPACER, self.location[1]+self.LV_3

   def draw(self):
      StatusBox.draw(self)

      text = "/ %i" % self.hpBar.maxValue
      textWidth = self.font.calcWidth(text)
      self.font.writeText(text, self.screen, (self.hpTextLocation[0]-textWidth, self.hpTextLocation[1]))
      
      self.font.writeText(str(self.hpBar.value), self.screen, (self.hpTextLocation[0]-textWidth-16, self.hpTextLocation[1]))
      

class EnemyStatusBox(StatusBox):
   LEFT_SPACER = 8
   RIGHT_SPACER = 13

   LV_1 = 5
   LV_2 = 15
   
   def __init__(self, screen, battleNode, poke):
      StatusBox.__init__(self, screen, battleNode, poke)
      
      enemypokemonNode = battleNode.getChild("enemypokemon")

      transparency = battleNode.getAttr("transparency", data.D_INT3LIST)

      fn = os.path.join(settings.path, "data", enemypokemonNode.getAttr("file", data.D_STRING))
      self.back = data.getImage(fn, battleNode.ditto_fn)
      self.back.set_colorkey(transparency)

      self.width = self.back.get_width()
      self.height = self.back.get_height()
      
      self.font = font.Font(os.path.join(settings.path, "data", battleNode.getAttr("statusfont", data.D_STRING)))

      self.font.writeText(poke.name, self.back, (self.LEFT_SPACER, self.LV_1))

      text = "Lv%i" % poke.level
      self.font.writeText(text, self.back, (self.width-self.font.calcWidth(text)-self.RIGHT_SPACER, self.LV_1))

   def setLocation(self, location, relative=(0,0)):
      StatusBox.setLocation(self, location, relative)

      self.hpBar.setLocation((self.width-self.hpBar.width-self.RIGHT_SPACER, self.LV_2), self.location)
      self.hpTextLocation = self.location[0]+56, self.location[1]+23

class HpBar():
   def __init__(self, screen, battleNode, maxValue):
      self.screen = screen

      self.location = (0,0)
      
      fn = os.path.join(settings.path, "data", battleNode.getAttr("hpbar", data.D_STRING))
      self.back = data.getImage(fn, "Hp bar image")
      transparency = battleNode.getAttr("transparency", data.D_INT3LIST)
      self.back.set_colorkey(transparency)

      self.width = self.back.get_width()

      self.maxValue = maxValue
      self.setValue(maxValue)

   def setLocation(self, location, relative=(0,0)):
      self.location = location[0]+relative[0], location[1]+relative[1]   

   def setValue(self, value):
      self.value = value
      self.updateSurface()

   def updateSurface(self):
      #calculate the width
      #unless we're set to 0, force the width to be a least 1
      barWidth = (HPBAR_SIZE[0]*self.value)/self.maxValue
      if self.value == 0:
         barWidth = 0
      else:
         if barWidth == 0:
            barWidth = 1

      #get the colour
      barMain, barShadow = self.getColours()
      voidMain, voidShadow = HPBAR_COLOURS[HPBAR_VOID]

      #fill the bar space black, then draw the bar over it
      pygame.draw.rect(self.back, voidShadow, (HPBAR_LOCATION[0], HPBAR_LOCATION[1], HPBAR_SIZE[0], HPBAR_SIZE[1]), 0)
      pygame.draw.rect(self.back, voidMain, (HPBAR_LOCATION[0], HPBAR_LOCATION[1]+1, HPBAR_SIZE[0], HPBAR_SIZE[1]-1), 0)

      if barWidth != 0:
         pygame.draw.rect(self.back, barShadow, (HPBAR_LOCATION[0], HPBAR_LOCATION[1], barWidth, HPBAR_SIZE[1]), 0)
         pygame.draw.rect(self.back, barMain, (HPBAR_LOCATION[0], HPBAR_LOCATION[1]+1, barWidth, HPBAR_SIZE[1]-1), 0)

   def getColours(self):
      """
      Determine the bar's colour.

      Return a tuple of (mainColour, shadowColour)
      """

      #calculate what fraction of the bar we're at
      #choose a colour accordingly
      fraction = float(self.value)/self.maxValue
      if fraction >= 0.5:
         return HPBAR_COLOURS[HPBAR_HIGH]
      elif fraction >= 0.2:
         return HPBAR_COLOURS[HPBAR_MIDDLE]
      else:
         return HPBAR_COLOURS[HPBAR_LOW]

   def draw(self):
      self.screen.blit(self.back, self.location)
