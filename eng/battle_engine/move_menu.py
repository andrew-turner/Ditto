import os

import eng.settings
import eng.data
import eng.box
import eng.font
import eng.game_input

BORDER = 12

#move choices
MC_MOVE = 0
MC_CANCEL = 1

class MoveMenu():
   def __init__(self, screen, movemenuNode, battle):
      self.screen = screen
      self.battle = battle

      self.height = battle.dialog.height
      self.width = battle.dialog.width

      self.sideWidth = self.width/3
      self.mainWidth = self.width-self.sideWidth

      fn = os.path.join(settings.path, "data", movemenuNode.getAttr("font", data.D_STRING))
      self.font = font.Font(fn)

      self.boxFn = os.path.join(settings.path, "data", movemenuNode.getAttr("file", data.D_STRING))      
      self.mainBox = box.Box((self.mainWidth, self.height), self.boxFn)
      self.cursor = self.mainBox.removeSideCursor()
      self.cursorWidth = self.cursor.get_width()
      self.sideBoxes = {}

      #write the moves
      x1 = BORDER
      x2 = self.mainWidth/2
      y1 = BORDER
      y2 = self.height/2
      
      self.textPositions = ((x1, y1),
                            (x2, y1),
                            (x1, y2),
                            (x2, y2))
      for i in range(0, 4):
         m = battle.playerPoke.moves[i]
         if m is not None:
            p = (self.textPositions[i][0]+self.cursorWidth, self.textPositions[i][1])
            self.font.writeText(m.name, self.mainBox, p)

      self.currSelection = 0

      self.location = (0,0)
      self.mainLocation = (0,0)
      self.sideLocation = (0,0)

      self.callbacks = {MC_MOVE: None,
                        MC_CANCEL: None}

      self.visible = False

   def setLocation(self, location, relative=(0,0)):
      self.location = location[0]+relative[0], location[1]+relative[1]

      self.mainLocation = self.location
      self.sideLocation = self.location[0]+self.mainWidth, self.location[1]

   def getSideBox(self):
      try:
         return self.sideBoxes[self.currSelection]
      except KeyError:
         b = box.Box((self.sideWidth, self.height), self.boxFn)
         m = self.battle.playerPoke.moves[self.currSelection]
         
         self.font.writeText("PP", b, (BORDER, BORDER))
         text = "%i/%i" % (m.currPP, m.maxPP)
         self.font.writeText(text, b, (self.sideWidth-self.font.calcWidth(text)-BORDER, BORDER))

         self.sideBoxes[self.currSelection] = b
         return b

   def inputButton(self, button):
      if button == game_input.BT_A:
         func = self.callbacks[MC_MOVE]
         if func is not None:
            func(self.currSelection)

      elif button == game_input.BT_B:
         func = self.callbacks[MC_CANCEL]
         if func is not None:
            func()

      elif button == game_input.BT_UP:
         if self.currSelection >= 2:
            self.currSelection -= 2

      elif button == game_input.BT_DOWN:
         if self.currSelection < 2:
            self.currSelection += 2

      elif button == game_input.BT_LEFT:
         if self.currSelection % 2 == 1:
            self.currSelection -= 1
            
      elif button == game_input.BT_RIGHT:
         if self.currSelection % 2 == 0:
            self.currSelection += 1

   def draw(self):
      if self.visible:
         self.screen.blit(self.mainBox, self.mainLocation)
         self.screen.blit(self.getSideBox(), self.sideLocation)

         p = self.textPositions[self.currSelection]
         self.screen.blit(self.cursor, (self.mainLocation[0]+p[0], self.mainLocation[1]+p[1]))
