from . import widget

class Label(widget.Widget):
   def __init__(self, parent, text="", **kwargs):
      self.init(parent, **kwargs)

      self._text = text
      self._usedFont = self.font
      self.size = self._usedFont.calcWidth(self._text), self._usedFont.height

      self.colour = kwargs.get("colour", "main")

   @property
   def text(self):
      return self.text

   @text.setter
   def text(self, val):
      self._text = val
      self.size = self._usedFont.calcWidth(self._text), self._usedFont.height
      
   def preDraw(self):
      self._usedFont.writeText(self._text, self._screen, self._screenPosition, colour=self.colour)
