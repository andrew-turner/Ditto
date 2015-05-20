import os

import pygame

from . import tilemap
from . import camera
from . import game_input
from . import settings
from . import globs
from . import player
from . import pokemon
from . import items
from . import save
from . import sound
from . import scene
from . import menus
from . import data
from . import sprite
from . import script_engine
from . import battle_engine
from . import environment_objects
import eng.dialog as dialog
import eng.behaviours as behaviours
import eng.symbols as symbols

class Game(scene.Scene):
   """Class to manage the main game world."""
   
   def __init__(self, screen, savegame=None, initialInfo=None):
      """
      Open the save file (or make a new one) and create camera and script engine.

      screen - the screen to render to.
      sound - the sound manager.
      savegame - path to the save file to open, or None to start a new game.
      """

      #store variables for use later
      self.screen = screen

      #parse the game XML file
      fn = os.path.join(settings.path, "data", "game.xml")
      root = data.getTreeRoot(fn, "Ditto main")

      node = root.getChild("battle")
      globs.BATTLE = node.getAttr("file", data.D_FILENAME)
      node = root.getChild("behaviours")
      globs.BEHAVIOURS = node.getAttr("file", data.D_FILENAME)
      node = root.getChild("objects")
      globs.OBJECTS = node.getAttr("file", data.D_FILENAME)
      node = root.getChild("fieldeffects")
      globs.FIELDEFFECTS = node.getAttr("file", data.D_FILENAME)

      #create script engine and initialise variables
      self.scriptEngine = script_engine.ScriptEngine()
      self.scriptEngine.setup(self, symbols.Symbols(self))
      self.paused = False
      self.foregroundObject = None

      #init the environment object directory
      environment_objects.init()
      behaviours.init()

      #if there's a save, open it
      #else start a new game
      if savegame is not None:
         self.openSave(savegame, root)
      else:
         self.newGame(os.path.join(settings.path, "saves", "ditto.sav"), root, initialInfo)

      #put the player onto the map and play music
      self.map.sprites["PLAYER"] = self.player
      sound.playMusic(self.player.map.music)

      #create a camera and attach to the player
      self.camera = camera.Camera(screen)
      self.camera.attachTo(self.player)

      if settings.ACCELERATE_DEBUG:
         #enemyPoke = pokemon.Pokemon("DONPHAN", 50)
         #self.foregroundObject = battle_engine.WildBattle(self.screen, self.player, enemyPoke, self.map.environment, self.map.weather)
         pass
         

   def giveInput(self, inputData):
      """
      Take the input data from the input manager and store it.

      inputData - a 3-tuple of the keys currently down, the keys just pressed and the keys just released.
      """

      #store each list separately
      self.keysDown = inputData[0]
      self.keysJustPressed = inputData[1]
      self.keysJustReleased = inputData[2]

   def tick(self):
      """Advance the game one tick"""

      #if there's no active object, use input to update the main game world
      if self.foregroundObject is None:
         for key in self.keysJustPressed:
            if key == game_input.BT_SAVE:
               self.writeSave()
               sound.playEffect(sound.SD_SAVE)
            elif key == game_input.BT_A:
               self.player.investigate()
            elif key == game_input.BT_B:
               self.player.setRunning(True)
            elif key == game_input.BT_START:
               self.paused = True
               sound.playEffect(sound.SD_MENUOPEN)
               self.foregroundObject = menus.PauseMenu(self.screen, self)
            elif key == game_input.BT_DEBUG:
               enemyPoke = pokemon.Pokemon("DONPHAN", 50)
               self.foregroundObject = battle_engine.WildBattle(self.screen, self.player, enemyPoke, self.map.environment, self.map.weather)
               
         for key in self.keysJustReleased:
            if key == game_input.BT_B:
               self.player.setRunning(False)

         for key in self.keysDown:
            if key == game_input.BT_UP:
               if self.player.direction == sprite.DIR_UP:
                  self.player.walk(sprite.DIR_UP)
               else:
                  self.player.face(sprite.DIR_UP)
            elif key == game_input.BT_DOWN:
               if self.player.direction == sprite.DIR_DOWN:
                  self.player.walk(sprite.DIR_DOWN)
               else:
                  self.player.face(sprite.DIR_DOWN)
            elif key == game_input.BT_LEFT:
               if self.player.direction == sprite.DIR_LEFT:
                  self.player.walk(sprite.DIR_LEFT)
               else:
                  self.player.face(sprite.DIR_LEFT)
            elif key == game_input.BT_RIGHT:
               if self.player.direction == sprite.DIR_RIGHT:
                  self.player.walk(sprite.DIR_RIGHT)
               else:
                  self.player.face(sprite.DIR_RIGHT)

      #if there is an active object, feed keydowns to it
      #tick it and check whether it's finished or not
      else:
         for key in self.keysJustPressed:
            self.foregroundObject.inputButton(key)
         self.foregroundObject.tellKeysDown(self.keysDown)

         self.foregroundObject.tick()
         if not self.foregroundObject.busy:
            self.foregroundObject = None
            self.paused = False

      #if we're not paused, tick the script engine and map      
      if not self.paused:
         self.scriptEngine.tick()
         self.player.map.tick()
         self.camera.tick()

      #we've not been told to exit, so not done yet   
      done = False
      return done

   def makeDialog(self, text, showCursor, colour="main"):
      return dialog.Dialog(text, self.screen, showCursor, colour)

   def makeChoiceDialog(self, text, choices):
      return dialog.ChoiceDialog(text, self.screen, choices)

   def drawFrame(self):
      """Draw a frame to the screen."""

      #tell the camera to draw a frame
      #then if there is a foreground object get that drawn on top
      self.camera.drawFrame()
      if self.foregroundObject is not None:
         self.foregroundObject.draw()

   def openSave(self, fn, root):
      """
      Open a save file.

      fn - the path to the save file.
      root - the root <game> node.
      """

      #open the file for reading, load the save game, and close
      self.savegame = save.readSave(fn)

      #create the current map and load its connections
      self.map = tilemap.Tilemap(self.savegame.currentMap)
      self.map.loadConnections()

      #create the player
      playerNode = root.getChild("player")
      if self.savegame.variables["GENDER"] == "FEMALE":
         genderNode = playerNode.getChild("female")
      else:
         genderNode = playerNode.getChild("male")
      self.player = player.Player(genderNode, self.map, self.savegame.currentPosition, self.savegame.currentLevel)
      self.player.direction = self.savegame.currentDirection

      #party
      self.party = self.savegame.party

      #bag
      self.bag = self.savegame.bag

   def writeSave(self):
      """Write the save file."""

      #store required data in savegame
      self.savegame.currentMap = self.player.map.id
      self.savegame.currentPosition = self.player.position
      self.savegame.currentLevel = self.player.level
      self.savegame.currentDirection = self.player.direction
      self.savegame.party = self.party
      self.savegame.bag = self.bag

      #open the file for writing, dump the save game, and close
      save.writeSave(self.savegame)

      print("Game saved to " + self.savegame.fn)

   def newGame(self, fn, root, initialInfo):
      """Start a new game"""

      #create the new save file
      self.savegame = save.Save(fn)
      for k in initialInfo:
         self.savegame.setVar(k, initialInfo[k])

      #get the new game node from the game xml file
      newgameNode = root.getChild("newgame")

      #create the map, loading connections since it's the active one
      self.map = tilemap.Tilemap(newgameNode.getAttr("map", data.D_STRING))
      self.map.loadConnections()

      #create the player
      playerNode = root.getChild("player")
      if initialInfo.get("GENDER", "") == "FEMALE":
         genderNode = playerNode.getChild("female")
      else:
         genderNode = playerNode.getChild("male")
      self.player = player.Player(genderNode,
                                  self.map,
                                  newgameNode.getAttr("position", data.D_INT2LIST),
                                  newgameNode.getAttr("level", data.D_INT))

      #create extras
      self.party = pokemon.Party()
      self.bag = items.Bag()

      #if there's a new game script, run it
      script = newgameNode.getOptionalChild("script")
      if script is not None:
         s = script_engine.scriptFromNode(script)
         self.scriptEngine.run(s)
      
