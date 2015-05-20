import os

import pygame

from . import foreground_object
from . import box
from . import font
from . import globs
from . import settings
from . import data
from . import sound
from . import game_input
import eng.script_engine as script_engine

#line separator in input text
LINESEP = "$$"

#define spacings
LINEBUFFER = 2 #spacing between lines
OBJECTBUFFER = 2 #spacing between boxes and edges

class Dialog(foreground_object.ForegroundObject):
   """
   Class to provide dialogs to be shown by the script engine.
   """
   
   def __init__(self, text, screen, drawCursor=True, colour="main"):
      """
      Create the dialog box and load cursors.

      text - a list of lines of text to go in the dialog.
      font - the font with which to write the text.
      screen - the surface to draw the dialog onto.
      soundManager - the sound manager.
      drawCursor - whether a continuation cursor should be drawn when the text has finished writing.
      colour - the colour of the writing.
      """

      #store variables we'll need again
      self.text = str(text)
      self.screen = screen
      self.drawCursor = drawCursor
      self.colour = colour
      
      #determine the speed to write at, in characters per tick
      if settings.textSpeed == "SLOW":
         self.speed = 1
      elif settings.textSpeed == "MEDIUM":
         self.speed = 2
      elif settings.textSpeed == "FAST":
         self.speed = 4

      #parse the dialog xml file
      root = data.getTreeRoot(globs.BOX, "Ditto main")
      transparency = root.getAttr("transparency", data.D_INT3LIST)

      #create font
      self.font = font.Font(globs.FONT)

      #box
      self.box = box.Box((10,10))
      self.xBorder = self.box.xBorder
      self.yBorder = self.box.yBorder

      #create the box
      numLines = max(len(self.text.split(font.LINESEP)), 2)
      size = (self.screen.get_width()-(OBJECTBUFFER*2),
              (numLines*(self.font.height+LINEBUFFER))-LINEBUFFER+(self.yBorder*2))
      self.box = self.box.resized(size)

      #get cursors
      self.cursor = self.box.cursor
      self.sideCursor = self.box.sideCursor

      #calculate location of dialog box
      self.location = OBJECTBUFFER, self.screen.get_height()-self.box.get_height()-OBJECTBUFFER
      self.cursorLocation = (self.location[0]+self.box.get_width()-self.xBorder-self.cursor.get_width(),
                             self.location[1]+self.box.get_height()-self.yBorder-self.cursor.get_height())

      #start progress at 0 and set drawing and busy
      self.progress = 0
      self.writing = True
      self.busy = True

   def draw(self):
      """Draw the dialog onto its screen."""

      #if we haven't finished writing the text, then write up to however far we've got
      if self.progress <= len(self.text)+1:
         self.font.writeText(self.text, self.box, (self.xBorder, self.yBorder), chars=self.progress,
                                                                                colour=self.colour,
                                                                                spacer=LINEBUFFER)

      #draw the box
      self.screen.blit(self.box, self.location)

      #if we've finished writing and a cursor is required, draw it
      if not self.writing and self.drawCursor:
         self.screen.blit(self.cursor, self.cursorLocation)

   def inputButton(self, button):
      """
      Process a button press

      button - the button which has been pressed.
      """

      #if it's the confirm button, and we've finished drawing, then we're done                          
      if button == game_input.BT_A:
         if not self.writing:
            self.busy = False
            sound.playEffect(sound.SD_SELECT)

   def tick(self):
      """Update the dialog one frame"""

      #increase the progress, and if we've reached the end the set drawing to False                      
      self.progress += self.speed
      if self.progress > sum(map(len, self.text)):
         self.writing = False

class ChoiceDialog(Dialog):
   """
   Adds a choice box to a dialog.

   Returns the choice selected to the LASTRESULT script engine variable.
   """
   
   def __init__(self, text, screen, choices):
      """
      Initialize the dialog and create the choice box.

      text - a list of lines of text to go in the dialog.
      font - the font with which to write the text.
      screen - the surface to draw the dialog onto.
      scriptEngine - the engine to return the option chosen to.
      choices - the possible options to choose from.
      """

      #initialize the dialog
      Dialog.__init__(self, text, screen, False)

      #store variables we'll need again
      self.choices = [str(choice) for choice in choices]

      #create script engine
      self.scriptEngine = script_engine.ScriptEngine()

      #create the choice box and write the options onto it
      maxWidth = max(list(map(self.font.calcWidth, self.choices)))
      size = (maxWidth+(self.xBorder*2)+self.sideCursor.get_width(),
              ((self.font.height+LINEBUFFER)*len(self.choices))-LINEBUFFER+(self.yBorder*2))
      self.choiceBox = box.Box(size).convert(self.screen)

      for i in range(0, len(self.choices)):
         choice = self.choices[i]
         location = (self.xBorder+self.sideCursor.get_width(),
                     self.yBorder+(i*(self.font.height+LINEBUFFER)))
         self.font.writeText(choice, self.choiceBox, location)

      #calculate the location of the choice box
      self.choiceLocation = (self.screen.get_width()-self.choiceBox.get_width()-OBJECTBUFFER,
                             self.location[1]-self.choiceBox.get_height()-OBJECTBUFFER)

      #set the current selected option to the first one
      self.current = 0

   def draw(self):
      """Draw the dialog, and choice box if required, onto its screen."""

      #draw the dialog
      Dialog.draw(self)

      #if the dialog has finished writing, draw the choice box and its cursor
      if not self.writing:
         self.screen.blit(self.choiceBox, self.choiceLocation)
         cursorLocation = (self.choiceLocation[0]+self.xBorder,
                           self.choiceLocation[1]+self.yBorder+(self.current*(self.font.height+LINEBUFFER)))
         self.screen.blit(self.sideCursor, cursorLocation)

   def inputButton(self, button):
      """
      Process a button press.

      button - the button which has been pressed.
      """

      #feed the button to the main dialog to process
      Dialog.inputButton(self, button)

      #if it's UP or DOWN, change the selected option as required
      if not self.writing:
         if button == game_input.BT_DOWN:
            if self.current < len(self.choices)-1:
               self.current += 1
               sound.playEffect(sound.SD_CHOOSE)
         elif button == game_input.BT_UP:
            if self.current > 0:
               self.current -= 1
               sound.playEffect(sound.SD_CHOOSE)

      #if we're exiting, set the LASTRESULT script engine variable to the current selected choice      
      if self.busy == False:
         self.scriptEngine.symbols.locals["LASTRESULT"] = self.choices[self.current]
