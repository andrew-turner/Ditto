import os

import eng.data
import eng.box
import eng.settings
import eng.font
import eng.game_input
import eng.dialog as dialog

#define spacings
BORDER = 12 #spacing inside the box
LINEBUFFER = 2 #spacing between lines

class BattleDialog(dialog.Dialog):
   def __init__(self, screen, battledialogNode, width):
      self.screen = screen      
      self.width = width

      self.drawCursor = False
      self.cursor = None

      self.text = ""

      #determine the speed to write at, in characters per tick
      if settings.textSpeed == "SLOW":
         self.speed = 1
      elif settings.textSpeed == "MEDIUM":
         self.speed = 2
      elif settings.textSpeed == "FAST":
         self.speed = 4

      #create font
      fn = os.path.join(settings.path, "data", battledialogNode.getAttr("font", data.D_STRING))
      self.font = font.Font(fn)

      #determine height
      self.height = (BORDER*2)+(self.font.height*2)+LINEBUFFER

      #create the box
      self.boxFn = os.path.join(settings.path, "data", battledialogNode.getAttr("file", data.D_STRING))      
      self.box = box.Box((self.width, self.height), self.boxFn)

      self.location = 0,0
      
      self.progress = 0
      self.writing = False
      self.busy = False

   def setLocation(self, location, relative=(0,0)):
      self.location = location[0]+relative[0], location[1]+relative[1]

   def setText(self, text):
      self.box = box.Box((self.width, self.height), self.boxFn)
      
      self.text = text.split(dialog.LINESEP)

      self.progress = 0
      self.writing = True
      self.busy = True



