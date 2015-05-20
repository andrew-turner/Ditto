from . import widget

class ImageSet(widget.Widget):
   def __init__(self, parent, fn, numImages, **kwargs):
      self.init(parent, **kwargs)

      self._numImages = numImages
      self._frames = []

      im = self._openImage(fn)
      self.size = (((im.get_width()+1)/numImages)-1,
                   im.get_height())
      for i in range(0, numImages):
         self._frames.append(im.subsurface((((self.size[0]+1)*i),0), self.size))
      
      self._imageNumber = 0

   @property
   def imageNumber(self):
      return self._imageNumber

   @imageNumber.setter
   def imageNumber(self, val):
      self._imageNumber = val % self._numImages

   @property
   def currentImage(self):
      return self._frames[self._imageNumber]

   def preDraw(self):
      self._screen.blit(self.currentImage, self._screenPosition)
      
