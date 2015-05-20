import pygame

import eng.data as data

NW = 0
NE = 1
SW = 2
SE = 3
N = 4
S = 5
W = 6
E = 7
C = 8

class Widget(object):
   """
   Widget class for interfaces.

   Inherits from object so we can use property decorators.

   Inherited by Interface class, the standard widgets, and any user defined widgets.
   """
   
   def __init__(self, parent, **kwargs):
      """
      Init method to be overridden when subclassed.

      Call to self.init(parent, **kwargs) should be made as soon as possible.

      parent - the parent widget.
      """

      #by default just call the widget init method
      self.init(parent, **kwargs)
   
   def init(self, parent, **kwargs):
      """
      Init the widget.

      Should be called ASAP from any overridden __init__ method.

      parent - the parent widget.
      
      optional keywords:
        position - the position of the widget, relative to the parent.
        background - the path to an image to use as the background.
        transparency - a colour to use as transparent.
        size - the size of the widget, if unspecified uses the size of background image, else (0,0).
        z - the z-ordering value, defaults to 0. Higher numbers are drawn on top.
        font - the font to use for any text, if unspecified looks through parents for one.
      """        
      
      #store parent and screen
      self._parent = parent
      self._screen = self._parent._screen

      #for child widgets
      self._childWidgets = []
      self._currentWidget = None
      self._inputObject = None

      #position
      #local position is position relative to parent
      #calling _updatePosition calculates the actual screen position, as long as the parent's screen position is defined.
      pos = kwargs.get("position", None)
      if pos is not None:
         self.setPosition(pos, kwargs.get("anchor", NW))
      else:
         self._localPosition = None
         self._screenPosition = None

      #z ordering
      #higher z means widget is drawn later, so displays on top
      #default to 0
      self.z = kwargs.get("z", 0)

      #transparency, must be set before opening any images
      self._transparency = kwargs.get("transparency", None)

      #background and sizing
      #if we have a background image, open it. If size is given use that, else use background size, else size is (0,0)
      self._backFn = kwargs.get("background", None)
      self.size = kwargs.get("size", None)
      if self._backFn is not None:
         self._back = self._openImage(self._backFn)
         if self.size is None:
            self.size = self._back.get_size()
      else:
         self._back = None
         if self.size is None:
            self.size = (0, 0)

      #store the font if given.
      self._font = kwargs.get("font", None)

      #initialise widget variables
      self.visible = True
      self.hasFocus = False

      #set busy to false by default
      self.busy = False

   def addWidget(self, w, pos=None, **kwargs):
      """
      Add a child widget to this one.

      w - the widget to add.
      pos - the position to set it at. If unset will assume the child widget already knows its position.
      """

      #if a position is given, tell the widget
      if pos is not None:
         w.setPosition(pos, kwargs.get("anchor", NW))

      #add to list of child widgets
      self._childWidgets.append(w)

   def removeWidget(self, w):
      """
      Remove a child widget from this one.

      w - the widget to remove.
      """

      #remove from the list if it's there
      #don't worry if it isn't
      try:
         self._childWidgets.remove(w)
      except ValueError:
         pass

      #if the widget was the input object, then we no longer have an input object
      if self._inputObject == w:
         self._inputObject = None

   @property
   def parent(self):
      return self._parent

   @property
   def position(self):
      """Return the position of the widget relative to its parent."""
      return self._localPosition

   @position.setter      
   def position(self, val):
      """Set the position of the widget relative to its parent."""

      #update local position and try to calculate screen position
      self._localPosition = val
      self._updatePosition()

   @property
   def x(self):
      """Return the position x coordinate."""
      return self._localPosition[0]

   @x.setter
   def x(self, val):
      self._localPosition = (val, self._localPosition[1])
      self._updatePosition()

   @property
   def y(self):
      """Return the position y coordinate."""
      return self._localPosition[1]

   @y.setter
   def y(self, val):
      self._localPosition[1] = (self._localPosition[0], val)
      self._updatePosition()

   def setPosition(self, position, anchor=NW):
      if not (isinstance(position, tuple) and len(position) == 2):
         #raise error
         raise ValueError
      
      if anchor == NW:
         self._localPosition = position
      elif anchor == NE:
         self._localPosition = position[0]-self.width, position[1]
      elif anchor == SW:
         self._localPosition = position[0], position[1]-self.height
      elif anchor == SE:
         self._localPosition = position[0]-self.width, position[1]-self.height
      elif anchor == N:
         self._localPosition = position[0]-(self.width/2), position[1]
      elif anchor == S:
         self._localPosition = position[0]-(self.width/2), position[1]-self.height
      elif anchor == W:
         self._localPosition = position[0], position[1]-(self.height/2)
      elif anchor == E:
         self._localPosition = position[0]-self.width, position[1]-(self.height/2)
      elif anchor == C:
         self._localPosition = position[0]-(self.width/2), position[1]-(self.width/2)

      self._updatePosition()

   def _updatePosition(self):
      """
      Update the screen position of the widget.

      Sets to None if local position or parent's screen position not known.
      """

      #if we have the required information, calculate the screen position
      #propagate through all child widgets
      if self._localPosition is not None and self._parent._screenPosition is not None:
         self._screenPosition = (self._parent._screenPosition[0]+self._localPosition[0],
                                 self._parent._screenPosition[1]+self._localPosition[1])
         for w in self._childWidgets:
            w._updatePosition()

      #otherwise set to None
      else:
         self._screenPosition = None

   @property
   def width(self):
      return self.size[0]

   @width.setter
   def width(self, val):
      self.size = val, self.size[1]

   @property
   def height(self):
      return self.size[1]

   @height.setter
   def height(self, val):
      self.size = self.size[0], val

   @property
   def font(self):
      """Get the font."""
      return self._findFont()

   @font.setter
   def font(self, val):
      """Set the font."""
      self._font = val

   def _findFont(self):
      """
      Search for a font to use.

      If we don't have one, get the parent to find out for us, unless we have no parent, in which case raise an error.
      """

      #if we have a font, return it
      if self._font is not None:
         return self._font

      #if we have a parent, get it to find us a font
      if self._parent is not None:
         return self._parent._findFont()

      #if that hasn't worked, raise an exception
      raise ValueError #NB need a better exception

   @property
   def transparency(self):
      if self._transparency is not None:
         return self._transparency

      if self._parent is not None:
         return self._parent.transparency

      raise ValueError

   @transparency.setter
   def transparency(self, value):
      self._transparency = value

   def _openImage(self, fn):
      """
      Open an image for the widget to use.

      Sets transparency if we have it.

      fn - the path to the image file.
      """

      #get the image and if possible set the transparency, then return the image
      im = data.getImage(fn, "Widget.")
      if self.transparency is not None:
         im.set_colorkey(self.transparency)
      return im
   
   def _inputButton(self, button):
      """
      Deal with a button press.

      button - the button.
      """

      #delegate to onInputButton hook
      self.onInputButton(button)

   def onInputButton(self, button):
      """
      Hook to deal with button presses.

      button - the button which was pressed.
      """

      #do nothing
      pass

   def _draw(self):
      """Draw the widget to the screen."""

      #if we're visible
      if self.visible:

         #if we have a background image, draw it
         if self._back is not None:
            self._screen.blit(self._back, self._screenPosition)

         #hook for drawing before child widgets
         self.preDraw()

         #draw child widgets
         for w in sorted(self._childWidgets, key=lambda w: w.z):
            w._draw()

         #hook for drawing after child widgets
         self.postDraw()

   def preDraw(self):
      """Hook to draw before child widgets."""

      #do nothing
      pass

   def postDraw(self):
      """Hook to draw after child widgets."""

      #do nothing
      pass

   def _destroyWidget(self, w):
      try:
         self._childWidgets.remove(w)
      except ValueError:
         pass

   def destroy(self):
      self.busy = False
      self._parent._destroyWidget(self)

   def _tick(self):
      """Tick the widget."""

      #hook to tick the widget
      self.onTick()

      #tick all child widgets
      for w in self._childWidgets:
         w._tick()

   def onTick(self):
      """Hook to tick the widget."""

      #do nothing
      pass
