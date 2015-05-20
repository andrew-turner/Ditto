from . import widget

import eng.box as box
import eng.settings as settings

class Message(widget.Widget):
   def __init__(self, parent, text="", fn=None, **kwargs):
      self.init(parent, **kwargs)

      self._text = text

      self._border = kwargs.get("border", 8)
      self._spacer = kwargs.get("spacer", 1)
      self._padding = kwargs.get("padding", 0)
      self.colour = kwargs.get("colour", "main")
      self._instant = kwargs.get("instant", True)
      self._speed = kwargs.get("speed", settings.textSpeed)

      defaultSize = (kwargs.get("width", self._parent.width),
                     kwargs.get("height", (self.font.height*2)+(self._border*2)+self._spacer+(self._padding*2)))
      self.size = kwargs.get("size", defaultSize)
      

      boxSize = (self.size[0]-(self._padding*2),
                 self.size[1]-(self._padding*2))
      self._box = box.Box(boxSize, fn)

      self._progress = 0
      self._finished = self._instant

   @property
   def text(self):
      return self._text

   @text.setter
   def text(self, value):
      self._text = value

      self._progress = 0
      self._finished = self._instant

   @property
   def finished(self):
      return self._finished

   def preDraw(self):
      boxPos = (self._screenPosition[0]+self._padding,
                self._screenPosition[1]+self._padding)
      
      textPos = (boxPos[0]+self._border,
                 boxPos[1]+self._border)

      self._screen.blit(self._box, boxPos)
      
      if self._finished:
         self.font.writeText(self._text, self._screen, textPos, colour=self.colour,
                                                                spacer=self._spacer)
      else:
         self.font.writeText(self._text, self._screen, textPos, chars=self._progress,
                                                                colour=self.colour,
                                                                spacer=self._spacer)

   def onTick(self):
      if not self._finished:
         self._progress += 1
         if self._progress > len(self._text):
            self._finished = True
