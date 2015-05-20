import os

import eng.interface as interface
import eng.settings as settings
import eng.font as font
from . import common
from . import resources

from eng.constants.buttons import *

class TestMenu(interface.Interface):
   def __init__(self, screen, context, game):
      self.init(screen, background=os.path.join(settings.path, "data", "graphics/bag.bmp"),
                        transparency=(255,0,255))

      self.font = font.Font(os.path.join(settings.path, "data", "fonts/font1.xml"))

      self.box = interface.Image(self, os.path.join(settings.path, "data", "graphics/partymain.bmp"), position=(30,30))
      self.addWidget(self.box)

      self.label = interface.Label(self, "Test label.")
      self.addWidget(self.label, (10,10))

      self.anim = interface.AnimatedImage(self, os.path.join(settings.path, "data", "pokemon/icons/025.bmp"), 2, ticksPerFrame=10)
      self.addWidget(self.anim, (20,20))

      fn = os.path.join(settings.path, "data", "graphics/HPbar.bmp")
      self.hpBar = common.HpBar(self, 100, value=78, background=fn)
      self.addWidget(self.hpBar, (100,40))

      fn = os.path.join(settings.path, "data", "graphics/bags.bmp")
      self.bag = interface.ImageSet(self, fn, 3)
      self.addWidget(self.bag, (10,80))

      self.msg = interface.Message(self, "What would you like to do?", resources.BOXPATH, padding=2)
      self.msg.setPosition((self.width/2,self.height), interface.S)
      self.addWidget(self.msg)

   def inputButton(self, button):
      if button == BT_B:
         self.busy = False

