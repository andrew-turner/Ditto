import os

from . import widget

class Interface(widget.Widget):
   def __init__(self, screen, context=(None, None), **kwargs):
      self.init(screen, context, **kwargs)
   
   def init(self, screen, context=(None, None), **kwargs):      
      #store variables for later
      self._screen = screen
      self.context, self.caller = context

      #transparency
      self._transparency = kwargs.get("transparency", None)

      #background and sizing   
      self._backFn = kwargs["background"]
      self._back = self._openImage(self._backFn)
      self.size = self._back.get_size()

      #positioning
      self._screenPosition = ((self._screen.get_width()-self.size[0])/2,
                              (self._screen.get_height()-self.size[1])/2)

      #font
      self._font = kwargs.get("font", None)

      #initialise widget list
      self._childWidgets = []
      self._currentWidget = None

      #no foreground object yet, and set busy
      self.foregroundObject = None
      self._inputObject = None
      self.keysDown = []
      self.busy = True
      self.visible = True

   def giveFocus(self, w):
      if self.currentWidget is None:
         self.currentWidget = w
         w.takeFocus()
      elif self.currentWidget == w:
         pass
      else:
         self.currentWidget.loseFocus()
         self.currentWidget = w
         w.takeFocus()

   def _findFont(self):
      if self._font is not None:
         return self._font
      else:
         raise ValueError

   def inputButton(self, button):
      if self.foregroundObject is not None:
         self.foregroundObject.inputButton(button)

      elif self._inputObject is not None:
         self._inputObject._inputButton(button)

      else:
         widget.Widget._inputButton(self, button)

   def tellKeysDown(self, keys):
      self.keysDown = keys

   def draw(self):
      if self.foregroundObject is not None:
         self.foregroundObject.draw()

      else:
         widget.Widget._draw(self)

   def tick(self):
      if self.foregroundObject is not None:
         self.foregroundObject.tick()
         if not self.foregroundObject.busy:
            self.foregroundObject = None

      widget.Widget._tick(self)

   def quitAll(self):
      self.busy = False
      if self.caller is not None:
         self.caller.quitAll()







      
