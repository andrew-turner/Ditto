import os

import eng.data
import eng.settings
import eng.box
import eng.font
import eng.game_input

#define spacings
BORDER = 12 #spacing inside the box
LINEBUFFER = 2 #spacing between lines

#battle choices
BC_FIGHT = 0
BC_POKEMON = 1
BC_BAG = 2
BC_RUN = 3

class BattleMenu():
   def __init__(self, screen, battlemenuNode, battle):
      self.screen = screen

      self.height = battle.dialog.height
      self.width = battle.dialog.width/2
      
      fn = os.path.join(settings.path, "data", battlemenuNode.getAttr("font", data.D_STRING))
      self.font = font.Font(fn)

      fn = os.path.join(settings.path, "data", battlemenuNode.getAttr("file", data.D_STRING))      
      self.box = box.Box((self.width, self.height), fn)
      self.cursor = self.box.removeSideCursor()

      self.x1 = BORDER
      self.x2 = (self.width/2)
      self.y1 = BORDER
      self.y2 = self.height/2
      cursorWidth = self.cursor.get_width()+1

      self.cursorLocations = {BC_FIGHT: (self.x1,self.y1),
                              BC_POKEMON: (self.x1,self.y2),
                              BC_BAG: (self.x2,self.y1),
                              BC_RUN: (self.x2,self.y2)}
      textLocations = [(x+cursorWidth, y) for (x,y) in list(self.cursorLocations.values())]
                                  
      self.font.writeText("FIGHT", self.box, textLocations[0])
      self.font.writeText("POKEMON", self.box, textLocations[1])
      self.font.writeText("BAG", self.box, textLocations[2])
      self.font.writeText("RUN", self.box, textLocations[3])
      
      self.location = 0,0
      self.visible = False
      self.active = True

      self.currSelection = BC_FIGHT
      
      self.callbacks = {BC_FIGHT: None,
                        BC_POKEMON: None,
                        BC_BAG: None,
                        BC_RUN: None}

   def setLocation(self, location, relative=(0,0)):
      self.location = location[0]+relative[0], location[1]+relative[1]

   def getCursorLocation(self):
      return self.cursorLocations[self.currSelection]

   def inputButton(self, button):
      if button == game_input.BT_A:
         func = self.callbacks[self.currSelection]
         if func is not None:
            func()
            
      elif button == game_input.BT_UP:
         if self.currSelection % 2 == 1:
            self.currSelection -= 1
            
      elif button == game_input.BT_DOWN:
         if self.currSelection % 2 == 0:
            self.currSelection += 1

      elif button == game_input.BT_LEFT:
         if self.currSelection >= 2:
            self.currSelection -= 2

      elif button == game_input.BT_RIGHT:
         if self.currSelection < 2:
            self.currSelection += 2
         

   def draw(self):
      if self.visible:
         self.screen.blit(self.box, self.location)

         cursorLocation = self.getCursorLocation()
         self.screen.blit(self.cursor, (self.location[0]+cursorLocation[0], self.location[1]+cursorLocation[1]))
