#! python3

import sys, os
import xml.etree.ElementTree as ET

import pygame

import eng.settings as settings
from . import game
from . import debug
from . import error
from . import error_handling
from . import globs
from . import intro
from . import game_input
from . import sound
from . import data
from . import pokemon
import eng.resource_ids as resource_ids
import eng.menus as menus

class Ditto():
   """Main entry class to create a Ditto game."""
   
   def setup(self):
      """Initialize pygame, find the main game file and parse it."""

      #initialise pygame
      pygame.init()

      #load plugins
      #plugins.loadAll()

      #find the main game file and parse it
      if settings.path is not None:
         fn = os.path.join(settings.path, "data", "main.xml")
      else:
         raise error.DittoInvalidResourceException("settings.py", "path")
      root = data.getTreeRoot(fn, "Ditto Main")

      node = root.getChild("tilesize")
      globs.TILESIZE = node.getAttr("size", data.D_INT2LIST)
      node = root.getChild("font")
      globs.FONT = node.getAttr("file", data.D_FILENAME)
      node = root.getChild("box")
      globs.BOX = node.getAttr("file", data.D_FILENAME)
      node = root.getChild("pokemon")
      globs.POKEMON = node.getAttr("file", data.D_FILENAME)
      node = root.getChild("moves")
      globs.MOVES = node.getAttr("file", data.D_FILENAME)
      node = root.getChild("natures")
      globs.NATURES = node.getAttr("file", data.D_FILENAME)
      node = root.getChild("types")
      globs.TYPES = node.getAttr("file", data.D_FILENAME)
      node = root.getChild("items")
      globs.ITEMS = node.getAttr("file", data.D_FILENAME)
      
      
      node = root.getChild("soundeffects")
      soundPath = node.getAttr("file", data.D_FILENAME)

      node = root.getChild("resources")
      resourcesPath = node.getAttr("file", data.D_FILENAME)

      node = root.getChild("menu")
      menuPath = os.path.join(settings.path, "data", node.getAttr("file", data.D_STRING))

      #if there's an icon specified, use it      
      if len(root.getChildren("icon")) > 0:
         node = root.getChild("icon")
         iconPath = node.getAttr("file", data.D_FILENAME)
         icon = data.getImage(iconPath, fn)
         pygame.display.set_icon(icon)

      #set up the main window
      windowSize = settings.screenSize[0]*globs.TILESIZE[0], settings.screenSize[1]*globs.TILESIZE[1]   
      self.screen = pygame.display.set_mode(windowSize)
      pygame.display.set_caption("%s --- Ditto Engine" % root.getAttr("title", data.D_STRING))

      #create a clock object
      self.clock = pygame.time.Clock()

      #initialise sound
      sound.init(soundPath)

      #init resources
      resource_ids.init(resourcesPath)

      menus.init(menuPath)

      #initialise pokemon
      pokemon.init(globs.NATURES)

      #set up the initial scene, the intro
      if settings.ACCELERATE_DEBUG:
         self.activeScene = game.Game(self.screen, os.path.join(settings.path, "saves", "ditto.sav"))
      else:
         self.activeScene = intro.Intro(self.screen)

   def mainloop(self):
      """Set Ditto's main loop going."""

      #until either we're done, or told to quit keep looping
      done = False
      quitEvent = False
      while not (done or quitEvent):
         #process any events, and give any input to the active scene
         quitEvent = game_input.processEvents()
         inputData = game_input.get()
         self.activeScene.giveInput(inputData)

         #tick the active scene
         done = self.activeScene.tick()

         #if the active scene is done, get the next one
         #if there is one, then we're not done yet
         if done:
            self.activeScene = self.activeScene.getNext()
            if self.activeScene is not None:
               done = False

         #draw the frame, and update the display
         self.activeScene.drawFrame()
         pygame.display.flip()
         
         #wait for the next frame
         if not game_input.BT_TURBO in inputData[0]:
            self.clock.tick(settings.framerate)

   def clearup(self):
      "Exit the game."""

      #quit pygame
      pygame.quit()
         

   def go(self):
      """Run the engine"""

      #try to run
      try:
         self.setup()
         self.mainloop()
         self.clearup()

      #if there's a Ditto exception raised, handle it specially   
      except error.DevError as e:
         try:
            error_handling.handleDevError(e, self.screen)
         except AttributeError:
            error_handling.handleDevError(e)

      #otherwise process it as a generic exception
      except Exception as e:
         try:
            error_handling.handleError(e, self.screen)
         except AttributeError:
            error_handling.handleError(e)
