from . import widget
from . import image

import eng.box as box
import eng.sound as sound

from eng.constants.buttons import *

class MiniMenu(widget.Widget):
   def __init__(self, parent, choices, fn=None, **kwargs):
      self.init(parent, **kwargs)

      self._options, self._args = list(zip(*choices))
      
      self._callback = kwargs.get("callback", None)
      self._border = kwargs.get("border", 0)
      self._linebuffer = kwargs.get("linebuffer", 1)
      self._safe = kwargs.get("safe", False)

      dummy = box.Box((10,10), fn)
      cursorWidth = dummy.sideCursor.get_width()

      maxWidth = max(list(map(self.font.calcWidth, self._options)))
      self.size = (maxWidth+cursorWidth+(self._border*2),
                  (len(self._options)*(self.font.height+self._linebuffer))-self._linebuffer+(self._border*2))
      self._box = box.Box(self.size, fn)

      pointerY = self._border
      for i in range(0, len(self._options)):
         self.font.writeText(self._options[i], self._box, (cursorWidth+self._border, pointerY))
         pointerY += self.font.height+self._linebuffer

      self.sideCursor = image.Image(self, self._box.sideCursor)
      self.addWidget(self.sideCursor, (self._border, self._border))

      self._current = 0

      self.busy = True

   def _positionCursor(self):
      self.sideCursor.position = (self._border,
                                  self._border+(self._current*(self.font.height+self._linebuffer)))

   def onInputButton(self, button):
      if button == BT_A:
         sound.playEffect(sound.SD_SELECT)
         if self._callback is not None:
            self._callback(self._args[self._current])
      elif button == BT_B and not self._safe:
         self.destroy()
      elif button == BT_UP:
         if self._current > 0:
            self._current -= 1
            sound.playEffect(sound.SD_CHOOSE)
            self._positionCursor()
      elif button == BT_DOWN:
         if self._current < len(self._options)-1:
            self._current += 1
            sound.playEffect(sound.SD_CHOOSE)
            self._positionCursor()

   def preDraw(self):
      self._screen.blit(self._box, self._screenPosition)
      
