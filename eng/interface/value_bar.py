import pygame

from . import widget

class ValueBar(widget.Widget):
   def __init__(self, parent, maxValue, **kwargs):
      self.init(parent, **kwargs)

      self.maxValue = maxValue
      self.value = kwargs.get("value", maxValue)
      self._dispValue = self.value

      self._voidColour = (kwargs.get("void", None),
                          kwargs.get("voidshadow", None))
      self._mainColour = (kwargs.get("main", None),
                          kwargs.get("mainshadow", None))
      self._extraColours = {}

      self._changeSpeed = kwargs.get("speed", 1)

   @property
   def moving(self):
      return (self._dispValue != self.value)

   def setVoidColour(self, col, shadow=None):
      self._voidColour = col, shadow

   def setMainColour(self, col, shadow=None):
      self._mainColour = col, shadow

   def setExtraColour(self, val, col, shadow=None):
      self._extraColours[val] = col, shadow

   def _getColours(self):
      fraction = float(self._dispValue)/self.maxValue
      ans = None
      for f in sorted(list(self._extraColours.keys()), reverse=True):
         if fraction <= f:
            ans = f

      if ans is not None:
         return self._extraColours[ans]
      else:
         return self._mainColour

   def preDraw(self):
      barWidth = (self.size[0]*self._dispValue)/self.maxValue
      if self._dispValue == 0:
         barWidth = 0
      else:
         if barWidth == 0:
            barWidth = 1

      #get the colour
      barMain, barShadow = self._getColours()
      voidMain, voidShadow = self._voidColour

      #fill the bar space void, then draw the bar over it
      pygame.draw.rect(self._screen, voidMain, (self._screenPosition, self.size), 0)
      if voidShadow is not None:
         pygame.draw.line(self._screen, voidShadow, self._screenPosition, (self._screenPosition[0]+self.size[0]-1, self._screenPosition[1]), 1)
      
      pygame.draw.rect(self._screen, barMain, (self._screenPosition, (barWidth, self.size[1])), 0)
      if barShadow is not None:
         pygame.draw.line(self._screen, barShadow, self._screenPosition, (self._screenPosition[0]+barWidth-1, self._screenPosition[1]), 1)

   def onTick(self):
      if self._dispValue != self.value:
         if self._dispValue-self.value > self._changeSpeed:
            self._dispValue -= self._changeSpeed
         elif self.value-self._dispValue > self._changeSpeed:
            self._dispValue += self._changeSpeed
         else:
            self._dispValue = self.value







      
