import os

import eng.interface as interface
import eng.data as data
import eng.font as font
from . import resources

from eng.constants.buttons import *

CX_PAUSE = 0

#NOTE
#trainer card should flip over, but there's no reason for it
#so it's not getting implemented for a while yet

class TrainerCard(interface.Interface):
   """The trainer card options on the pause menu."""
   
   def __init__(self, screen, context, game):
      """
      Create the trainer card image.

      screen - the screen to blit to.
      context - the context that we've been opened from.
      game - the current game.
      """

      #init
      cardNode = data.getTreeRoot(resources.getFilename(resources.I_TRAINERCARD), "Menu config.")
      fn = cardNode.getAttr("back", data.D_FILENAME)
      self.transparency = cardNode.getAttr("transparency", data.D_INT3LIST)
      
      self.init(screen, background=fn,
                        transparency=self.transparency)

      #font
      fn = cardNode.getAttr("font", data.D_FILENAME)
      self.font = font.Font(fn)

      #player's id
      text = "Idno.%s" % "TODO"
      l = interface.Label(self, text)
      self.addWidget(l, (152, 13))

      #player's name
      text = "Name:   %s" % game.savegame.getVar("PLAYERNAME")
      l = interface.Label(self, text)
      self.addWidget(l, (25, 32))

      #make the list of information to show
      #create the labels
      info = (("Money", "Y%i" % game.savegame.getVar("MONEY")),
              ("Pokedex", "TODO"),
              ("Time", "%i:%i" % (game.savegame.playtime / 60, game.savegame.playtime % 60)))

      pointerY = 60
      for title, value in info:
         l = interface.Label(self, title)
         self.addWidget(l, (25, pointerY))
         l = interface.Label(self, value)
         self.addWidget(l, (140, pointerY), anchor=interface.NE)
         pointerY += 16

      #TODO
      #pokedex number
      #trainer sprite

   def inputButton(self, button):
      """
      Process a button press.

      button - the button that was pressed.
      """

      #if it was the B button, exit
      if button == BT_B:
         self.busy = False

