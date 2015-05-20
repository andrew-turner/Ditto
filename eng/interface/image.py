import pygame

from . import widget

class Image(widget.Widget):
   def __init__(self, parent, im, **kwargs):
      self.init(parent, **kwargs)

      self._image = self._getImage(im)

      self.size = self._image.get_size()

   def _getImage(self, im):
      if isinstance(im, str):
         return self._openImage(im)

      if isinstance(im, pygame.Surface):
         return im

      #raise error
      raise TypeError

   def preDraw(self):
      self._screen.blit(self._image, self._screenPosition)
