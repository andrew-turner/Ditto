import os

import pygame

import eng.foreground_object as foreground_object
import eng.box as box
import eng.globs as globs
import eng.font as font
import eng.settings as settings
import eng.data as data
import eng.sound as sound

from . import party_screen
from . import bag_screen
from . import trainer_card
from . import resources
from . import test_menu
from . import map_screen

from eng.constants.buttons import *

PM_POKEDEX = 0
PM_PARTY = 1
PM_BAG = 2
PM_TRAINERCARD = 3
PM_SAVE = 4
PM_OPTIONS = 5
PM_EXIT = 6

class PauseMenu(foreground_object.ForegroundObject):
   """The pause menu."""
   
   def __init__(self, screen, game):
      """
      aa

      screen - the screen to blit to.
      game - the current game.
      fn - path to the menu xml file.
      """

      #store variables for later
      self.screen = screen
      self.game = game

      #create the font
      self.font = font.Font(globs.FONT)

      self.objectBuffer = 2
      self.lineBuffer = 3

      #create a list of choice tuples: (constant, text)
      #can't use a dict since we need ordering.
      self.choices = []
      if True: #has pokedex
         self.choices.append((PM_POKEDEX, "POKEDEX"))
      if self.game.party:
         self.choices.append((PM_PARTY, "POKEMON"))
      self.choices.append((PM_BAG, "BAG"))
      self.choices.append((PM_TRAINERCARD, self.game.savegame.getVar("PLAYERNAME")))
      self.choices.append((PM_SAVE, "SAVE"))
      self.choices.append((PM_OPTIONS, "OPTIONS"))
      self.choices.append((PM_EXIT, "EXIT"))

      #create the shadow to darken the world
      self.shadow = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
      self.shadow.fill((10,10,10))
      self.shadow.set_alpha(100)

      #dummy for side cursor width
      b = box.Box((10,10))
      self.sideCursor = b.sideCursor
      self.xBorder = b.xBorder
      self.yBorder = b.yBorder

      #create a list of the names for each option
      #use to determine the size of the menu
      names = [choice[1] for choice in self.choices]
      self.size = (max(list(map(self.font.calcWidth, names))) + self.xBorder*2 + self.sideCursor.get_width(),
                   (self.yBorder*2)+(self.font.height*len(self.choices))+(self.lineBuffer*(len(self.choices)-1)))
      
      #create the actual box
      self.box = b.resized(self.size)
      self.location = (self.screen.get_width()-self.size[0]-self.objectBuffer, self.objectBuffer)

      #write each choice onto the box
      i = 0
      for choice in self.choices:
         text = choice[1]
         location = (self.xBorder+self.sideCursor.get_width(),
                     (i*(self.font.height+self.lineBuffer))+self.yBorder)
         self.font.writeText(text, self.box, location)
         i += 1

      #side cursor
      self.sideCursor = self.box.sideCursor

      #start with top option
      self.current = 0

      #no foreground object yet
      self.foregroundObject = None

      #set busy
      self.busy = True

   def inputButton(self, button):
      if self.foregroundObject is None:
         if button == BT_A:
            self.choose(self.choices[self.current][0])
         elif button == BT_B:
            self.busy = False
         elif button == BT_UP:
            if self.current > 0:
               self.current -= 1
               sound.playEffect(sound.SD_CHOOSE)
         elif button == BT_DOWN:
            if self.current < len(self.choices)-1:
               self.current += 1
               sound.playEffect(sound.SD_CHOOSE)
      else:
         self.foregroundObject.inputButton(button)

   def tellKeysDown(self, keys):
      if self.foregroundObject is not None:
         self.foregroundObject.tellKeysDown(keys)

   def draw(self):
      if self.foregroundObject is None:
         self.screen.blit(self.box, self.location)
         self.screen.blit(self.sideCursor, (self.location[0]+self.xBorder,
                                            self.location[1]+self.yBorder+(self.current*(self.font.height+self.lineBuffer))))

      else:
         self.screen.blit(self.shadow, (0,0))
         self.foregroundObject.draw()

   def tick(self):
      if self.foregroundObject is not None:
         self.foregroundObject.tick()
         if not self.foregroundObject.busy:
            self.foregroundObject = None

   def choose(self, choice):
      if choice == PM_POKEDEX:
         self.foregroundObject = test_menu.TestMenu(self.screen, (None, self), self.game)
      
      if choice == PM_PARTY:
         self.foregroundObject = party_screen.PartyScreen(self.screen, (party_screen.CX_PAUSE, self), self.game)

      elif choice == PM_BAG:
         self.foregroundObject = bag_screen.BagScreen(self.screen, (bag_screen.CX_PAUSE, self), self.game)

      elif choice == PM_TRAINERCARD:
         self.foregroundObject = trainer_card.TrainerCard(self.screen, (trainer_card.CX_PAUSE, self), self.game)

      elif choice == PM_SAVE:
         self.foregroundObject = map_screen.MapScreen(self.screen, (map_screen.CX_PARTY_FLY, self), self.game)
         
      elif choice == PM_EXIT:
         self.busy = False
         
      else:
         print(choice)

   def quitAll(self):
      self.busy = False
