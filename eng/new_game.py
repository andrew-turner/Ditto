import os
import xml.etree.ElementTree as ET

import pygame

from . import settings
from . import scene
from . import sound
from . import game_input
from . import data
from . import text_split
from . import font
from . import interface
from .menus import text_input
from . import globs
from . import game
from .menus import resources
import eng.sound as sound

# will need to add a class which can handle moving of sprites

class NewGame(scene.Scene):
   """The main intro scene."""
   
   def __init__(self, screen):
      """
      Load all intro screens and start the first.

      screen - the screen to blit to.
      """

      #store screen for use later
      self.screen = screen

      self.foregroundObject = None

      #parse the intro XML file
      fn = os.path.join(settings.path, "data", "new_game.xml")
      root = data.getTreeRoot(fn, "New Game")

      self.font = font.Font(globs.FONT)

      #play music
      sound.playMusic(root.getAttr("music", data.D_FILENAME))

      # create a dictionary that will contain the info about the player (ie. gender, name)
      self.player_info = {}

      #create each intro screen
      self.screenNodes = [node for node in root.getChildren() if node.tag in ("screen", "inputscreen")]

      self.inputOption = None      

      #set the first screen active
      self.displayNextScreen()
      

   def displayNextScreen(self):
      node = self.screenNodes.pop(0)
      if node.tag == "screen":
         self.foregroundObject = Screen(self.screen, (None, self), node)
         self.inputOption = None
         
      elif node.tag == "inputscreen":
         text = node.getAttr("text", data.D_STRING)
         animFn = os.path.join(settings.path, "data", node.getAttr("anim", data.D_STRING).format(**self.player_info))         
         self.foregroundObject = text_input.TextInput(self.screen, (text_input.CX_NEWGAME, self), text, animFn)
         self.inputOption = node.getAttr("option", data.D_STRING)

      else:
         raise ValueError

   def giveInput(self, inputData):
      """
      Recieve input data.

      inputData - the input data 3-tuple.
      """

      #we're only bothered about keydowns
      self.keysJustPressed = inputData[1]

   def drawFrame(self):
      """Draw a frame to the screen."""

      self.screen.fill((0,0,50))

      #call on the active screen to draw itself
      self.foregroundObject.draw()

   def tick(self):
      """Update the intro one frame."""

      done = False
      #tick the active screen, find out whether it's done

      self.foregroundObject.tick()

      # pass button presses to the foreground object
      for button in self.keysJustPressed:
         self.foregroundObject.inputButton(button)

      #if button A has been pressed, the current screen is done
      done = self.foregroundObject.done

      #if the current screen is done, move on to the next
      #if there are no more, return True to say we're done
      #otherwise load the next one
      if done:
         if self.inputOption is not None:
            self.player_info[self.inputOption] = self.foregroundObject.value
         if self.screenNodes:
            self.displayNextScreen()
         else:
            return True            

      #we're still going
      return False

   def getNext(self):
      """Get the next game scene."""

      #return the new game
      return game.Game(self.screen, None, self.player_info)
      #return game_select.GameSelect(self.screen)

class Screen(interface.Interface):
   def __init__(self, screen, context, node):

      self.screen = screen

      self.done = False

      self.node = node

      self.the_parent = context[1]

      # get the background data
      bgNode = node.getChild("bg_image")
      bg = bgNode.getAttr("file", data.D_FILENAME)
      self.transparency = bgNode.getAttr("transparency", data.D_INT3LIST)
      
      self.init(screen, background=bg, transparency=self.transparency)

      self.font = font.Font(os.path.join(settings.path, "data", "fonts/font1.xml"))

      self.splitter = text_split.TextSplit(self.font)

      self.hasMiniMenu = False

      # first draw the shadow
      shadowNode = self.node.getOptionalChild("shadow")
      if shadowNode is not None:
         image_location = tuple(shadowNode.getAttr("location", data.D_INT2LIST))
         imagePath = shadowNode.getAttr("file", data.D_FILENAME)
         self.addWidget(interface.Image(self, imagePath, position=image_location,
                                                         z=-1))
      # sort out images
      for imageNode in self.node.getChildren("image"):
         self.option = self.the_parent.player_info.get(imageNode.getOptionalAttr("option", data.D_STRING))
         image_location = tuple(imageNode.getAttr("location", data.D_INT2LIST))
         imagePath = imageNode.getAttr("file", data.D_FILENAME).format(self.option)
         image = interface.Image(self, imagePath, position=image_location)
         self.addWidget(image)

      #text
      self.dialogNodes = [node for node in self.node.getChildren() if node.tag in ("dialog", "choicedialog")]

      self.msg = interface.Message(self, "", padding=2,
                                             instant=False)
      self.addWidget(self.msg)
      self.msg.setPosition((self.width/2,self.height), interface.S)

      self.displayNextDialog()

      self.miniMenu = None

   def displayNextDialog(self):
      if self.dialogNodes:
         node = self.dialogNodes.pop(0)

         self.msg.text = node.getAttr("text", data.D_STRING).format(**self.the_parent.player_info)

         if node.tag == "choicedialog":
            self.choice_option = node.getAttr("option", data.D_STRING)

            choices = []
            for choiceNode in node.getChildren("choice"):
               choices.append((choiceNode.getAttr("text", data.D_STRING), choiceNode.getAttr("set", data.D_STRING)))

               self.miniMenu = interface.MiniMenu(self, choices, callback=self.getChoice,
                                                                 border=7,
                                                                 safe=True)
               self.addWidget(self.miniMenu)
               self.miniMenu.setPosition((self.width-2, self.height-self.msg.height), anchor=interface.SE)
               self.miniMenu.visible = False

      else:
         self.done = True
            
         

   def inputButton(self, button):
      if (self.miniMenu is not None) and self.miniMenu.visible:
         self.miniMenu.onInputButton(button)
         if button == game_input.BT_A:
            self.removeWidget(self.miniMenu)
            self.miniMenu = None
            self.displayNextDialog()
      else:
         if ((button == game_input.BT_A) and
             self.msg.finished):
            self.displayNextDialog()

   def getChoice(self, choice):
      self.the_parent.player_info[self.choice_option] = choice

   def getDone(self):
      return self.done

   def onTick(self):
      if (self.miniMenu is not None) and self.msg.finished:
         self.miniMenu.visible = True
