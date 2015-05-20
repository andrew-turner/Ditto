import eng.interface as interface

HPBAR_LOCATION = 15, 2
HP_SIZE = 48, 3

HP_GREEN = ((112, 248, 168),
            (88, 208, 128))
HP_ORANGE = ((248, 224, 56),
             (200, 168, 8))
HP_RED = ((248, 88, 56),
          (168, 64, 72))
HP_VOID = ((80, 104, 88),
           (72, 64, 88))

class HpBar(interface.Widget):
   """HP bar widget."""
   
   def __init__(self, parent, maxValue, **kwargs):
      """
      Set up the image and draw in the first bar.

      parent - the widget's parent.
      location - the location  relative to the parent.
      maxValue - the highest value the widget will hold. Also the initial value.
      """

      #init the base widget
      self.init(parent, **kwargs)

      val = kwargs.get("value", maxValue)

      self.valueBar = interface.ValueBar(self, maxValue, value=val, size=HP_SIZE, speed=3)      
      self.valueBar.setVoidColour(*HP_VOID)
      self.valueBar.setMainColour(*HP_GREEN)
      self.valueBar.setExtraColour(0.5, *HP_ORANGE)
      self.valueBar.setExtraColour(0.1, *HP_RED)
      self.addWidget(self.valueBar, HPBAR_LOCATION)

   @property
   def value(self):
      return self.valueBar.value

   @value.setter  
   def value(self, val):
      """
      Set the bar's value and update graphics.

      value - the new value.
      """

      #set the new value and update
      self.valueBar.value = val

   @property
   def moving(self):
      return self.valueBar.moving
