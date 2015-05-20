from . import widget

class AnimatedImage(widget.Widget):
   def __init__(self, parent, fn, numFrames, **kwargs):
      self.init(parent, **kwargs)

      self._numFrames = numFrames
      self.ticksPerFrame = kwargs.get("ticksPerFrame", 1)
      self._frames = []

      im = self._openImage(fn)
      self.size = (((im.get_width()+1)/numFrames)-1,
                   im.get_height())
      for i in range(0, numFrames):
         self._frames.append(im.subsurface((((self.size[0]+1)*i),0), self.size))
      

      self._counter = 0
      self._frameNumber = 0

   @property
   def currentImage(self):
      return self._frames[self._frameNumber]

   def preDraw(self):
      im = self.currentImage
      if im is not None:
         self._screen.blit(im, self._screenPosition)

   def onTick(self):
      self._counter += 1
      if self._counter >= self.ticksPerFrame:
         self._counter = 0
         self._frameNumber += 1
         if self._frameNumber >= self._numFrames:
            self._frameNumber = 0
      
