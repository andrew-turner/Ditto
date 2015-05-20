import os
import xml.etree.ElementTree as ET

import pygame

import eng.settings as settings
import eng.scene as scene
import eng.sound as sound
import eng.game_input as game_input
import eng.data as data
import eng.text_split as text_split
import eng.font as font
import eng.interface as interface
import eng.menus.resources as resources
import eng.globs as globs
from eng.constants.buttons import *

#context
CX_NEWGAME = 0
CX_NICKNAME = 1

#keyboard callbacks
K_ADDCHAR = 0
K_DELCHAR = 1
K_DONE = 2

class TextInput(interface.Interface):
   def __init__(self, screen, context, text="", anim=None):

      #init
      fn = resources.getFilename(resources.I_TEXTINPUT)
      inputNode = data.getTreeRoot(fn, "Text input config.")
      fn = inputNode.getAttr("back", data.D_FILENAME)
      self.transparency = inputNode.getAttr("transparency", data.D_INT3LIST)
      
      self.init(screen, background=fn,
                        transparency=self.transparency)

      #random
      self.done = False
      self.active = False

      self.context, self.the_parent = context

      #font
      self.font = font.Font(globs.FONT)

      #text view
      textViewNode = inputNode.getChild("textview")
      self.textView = TextView(self, textViewNode, text, anim)
      self.addWidget(self.textView)
      self.textView.setPosition((int(self.width/2), 20), interface.N)

      #keyboard
      keyboardNode = inputNode.getChild("keyboard")
      callbacks = {K_ADDCHAR: self.textView.addChar,
                   K_DELCHAR: self.textView.delChar,
                   K_DONE: self.onKeyboardDone}
      self.keyboard = Keyboard(self, keyboardNode, callbacks)
      self.addWidget(self.keyboard)
      self.keyboard.setPosition((int(self.width/2), self.textView.y+self.textView.height+5), interface.N)
      
   def inputButton(self, button):
      self.keyboard.inputButton(button)

   @property
   def value(self):
      return self.textView.value

   def onKeyboardDone(self):
      if self.textView.value:
         self.done = True

class TextView(interface.Widget):

   MAXCHARS = 7

   TITLEPOSITION = (91, 8)
   ARROWPOSITION = (52, 24)
   ANIMPOSITION = (22, 28)
   
   def __init__(self, parent, node, text, anim):
      #init
      fn = node.getAttr("back", data.D_FILENAME)
      self.init(parent, background=fn)
      
      #arrow cursor
      cursorNode = node.getChild("cursor")
      fn = cursorNode.getAttr("file", data.D_FILENAME)
      self.arrow = interface.AnimatedImage(self, fn, 8)
      self.addWidget(self.arrow, self.ARROWPOSITION)

      #moving underscore
      underscoreNode = node.getChild("underscore")
      fn = underscoreNode.getAttr("file", data.D_FILENAME)
      self.underscore = interface.AnimatedImage(self, fn, 6, ticksPerFrame=2)
      self.addWidget(self.underscore)

      #title text
      self.title = interface.Label(self, text)
      self.addWidget(self.title)
      self.title.setPosition(self.TITLEPOSITION, interface.N)

      #anim image
      if anim is not None:
         self.anim = interface.AnimatedImage(self, anim, 4, ticksPerFrame=3)
         self.addWidget(self.anim)
         self.anim.setPosition(self.ANIMPOSITION, interface.S)

      #initialise variables
      self.cursorPosition = 0
      self.chars = []

      self.placeUnderscore()

   @property
   def value(self):
      return "".join([tup[0] for tup in self.chars])

   def addChar(self, char):
      if len(self.chars) < self.MAXCHARS:
         l = interface.Label(self, char)
         pos = (65 + (len(self.chars)*8),
                35)
         self.addWidget(l)
         l.setPosition(pos, interface.SW)
         
         self.chars.append((char, l))

         self.placeUnderscore()

   def delChar(self):
      if self.chars:
         char, l = self.chars.pop()
         self.removeWidget(l)

         self.placeUnderscore()

   def placeUnderscore(self):
      if len(self.chars) == self.MAXCHARS:
         self.underscore.visible = False
      else:
         self.underscore.position = (65 + (len(self.chars)*8),
                                     35)
         self.underscore.visible = True
             
      

class Keyboard(interface.Widget):
   def __init__(self, parent, node, callbacks):
      #init
      self.init(parent)
      
      #cursor
      fn = node.getAttr("cursor1", data.D_FILENAME)
      self.cursor = interface.AnimatedImage(self, fn, 4, ticksPerFrame=2,
                                                         z=1)
      self.addWidget(self.cursor, (0,0))

      fn = node.getAttr("cursor2", data.D_FILENAME)
      self.specialCursor = interface.AnimatedImage(self, fn, 4, ticksPerFrame=2,
                                                         z=1)
      self.addWidget(self.specialCursor, (0,0))

      self.cursorPosition = (0,0)

      #pages
      self.pages = (UpperPage(self, node.getChild("upper")),
                    LowerPage(self, node.getChild("lower")),
                    OtherPage(self, node.getChild("other")))
      self._currPageIndex = 0
      self.size = self.pages[0].size

      #load page
      self.addWidget(self.currPage, (0,0))

      self.placeCursor()

      #store callbacks
      self.callbacks = callbacks

   def loadPage(self):
      self.removeWidget(self.currPage)
      self.addWidget(self.pages[self.currPageIndex], (0,0))

   @property
   def currPageIndex(self):
      return self._currPageIndex

   @currPageIndex.setter
   def currPageIndex(self, val):
      self._currPageIndex = (self._currPageIndex + 1) % len(self.pages)

   @property
   def currPage(self):
      return self.pages[self.currPageIndex]

   def placeCursor(self):
      self.cursorPosition = self.currPage.correctGrid(self.cursorPosition)
         
      pos = self.currPage.gridToPixel(self.cursorPosition)

      if self.cursorPosition[0] <= 7:
         self.cursor.visible = True
         self.specialCursor.visible = False
         self.cursor.position = (pos[0]-3,
                                 pos[1]-4)
      else:
         self.cursor.visible = False
         self.specialCursor.visible = True
         self.specialCursor.position = pos

   def inputButton(self, button):
      if button == BT_A:
         if self.cursorPosition == (8, 0):
            self.currPageIndex += 1
            self.loadPage()
         elif self.cursorPosition == (8, 1):
            func = self.callbacks[K_DELCHAR]
            func()
         elif self.cursorPosition == (8, 2):
            func = self.callbacks[K_DONE]
            func()
         else:
            func = self.callbacks[K_ADDCHAR]
            func(self.currPage.charAt(self.cursorPosition))
      elif button == BT_B:
         func = self.callbacks[K_DELCHAR]
         func()
      elif button == BT_UP:
         if self.cursorPosition[1] > 0:
            self.cursorPosition = (self.cursorPosition[0],
                                   self.cursorPosition[1]-1)
      elif button == BT_DOWN:
         if self.cursorPosition[1] < 4-1:
            self.cursorPosition = (self.cursorPosition[0],
                                   self.cursorPosition[1]+1)
      elif button == BT_LEFT:
         if self.cursorPosition[0] > 0:
            self.cursorPosition = (self.cursorPosition[0]-1,
                                   self.cursorPosition[1])
      elif button == BT_RIGHT:
         if self.cursorPosition[0] < self.currPage.gridWidth-1:
            self.cursorPosition = (self.cursorPosition[0]+1,
                                   self.cursorPosition[1])
         elif self.cursorPosition[0] == self.currPage.gridWidth-1:
            self.cursorPosition = (8, self.cursorPosition[1])
            
      elif button == BT_START:
         self.cursorPosition = (8, 2)

      elif button == BT_SELECT:
         self.currPageIndex += 1
         self.loadPage()
            
      self.placeCursor()
      

class InputPage(interface.Widget):
   def __init__(self, parent, node):      
      self.init(parent)

      fn = node.getAttr("back", data.D_FILENAME)
      self.im = interface.Image(self, fn)
      self.addWidget(self.im, (0,0))
      self.size = self.im.size

   def gridToPixel(self, pos):
      raise NotImplementedError

   def correctGrid(self, pos):
      raise NotImplementedError

   def charAt(self, pos):
      row = self.CHARS[pos[1]]
      return row[pos[0]]

class UpperPage(InputPage):

   CHARS = ("ABCDEF .",
            "GHIJKL ,",
            "MNOPQRS ",
            "TUVWXYZ ")

   gridWidth = 8
   
   def __init__(self, parent, node):
      InputPage.__init__(self, parent, node)

   def gridToPixel(self, pos):
      #grid of
      # xxx xxxx x s
      # xxx xxxx x s
      # xxx xxxx x s
      # xxx xxxx x
      
      x, y = pos
      if x <= 7:
         if x <= 2:
            resX = 18 + (x*12)
         elif x <= 6:
            resX = 18 + 20 + (x*12)
         elif x <= 7:
            resX = 18 + 20 + 20 + (x*12)
         resY = 9 + (y*16)
      else:
         resX = 171
         if y == 0:
            resY = 2
         elif y == 1:
            resY = 31
         else:
            resY = 53

      return (resX, resY)

   def correctGrid(self, pos):
      if pos == (8, 3):
         return (8, 2)

      return pos    

class LowerPage(InputPage):

   CHARS = ("abcdef .",
            "ghijkl ,",
            "mnopqrs ",
            "tuvwxyz ")

   gridWidth = 8
   
   def __init__(self, parent, node):
      InputPage.__init__(self, parent, node)

   def gridToPixel(self, pos):
      #grid of
      # xxx xxxx x s
      # xxx xxxx x s
      # xxx xxxx x s
      # xxx xxxx x
      
      x, y = pos
      if x <= 7:
         if x <= 2:
            resX = 18 + (x*12)
         elif x <= 6:
            resX = 18 + 20 + (x*12)
         elif x <= 7:
            resX = 18 + 20 + 20 + (x*12)
         resY = 9 + (y*16)
      else:
         resX = 171
         if y == 0:
            resY = 2
         elif y == 1:
            resY = 31
         else:
            resY = 53

      return (resX, resY)

   def correctGrid(self, pos):
      if pos == (8, 3):
         return (8, 2)

      return pos

class OtherPage(InputPage):

   CHARS = ("01234 ",
            "56789 ",
            "!?xx/-",
            "xxxxx ")

   gridWidth = 6
   
   def __init__(self, parent, node):
      InputPage.__init__(self, parent, node)

   def gridToPixel(self, pos):
      #grid of
      # xxxxx s
      # xxxxx s
      # xxxxx s
      # xxxxx
      
      x, y = pos
      if x <= 7:
         resX = 18 + (x*22)
         resY = 8 + (y*16)
      else:
         resX = 171
         if y == 0:
            resY = 2
         elif y == 1:
            resY = 31
         else:
            resY = 53

      return (resX, resY)

   def correctGrid(self, pos):
      if pos == (8, 3):
         return (8, 2)

      if 6 <= pos[0] <= 7:
         return (5, pos[1])

      return pos

      


      
