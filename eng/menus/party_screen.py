import os

import pygame

import eng.interface as interface
import eng.foreground_object as foreground_object
import eng.box as box
import eng.globs as globs
import eng.settings as settings
import eng.font as font
import eng.pokemon as pokemon
from . import summary_screen
import eng.data as data
import eng.script_engine as script_engine
from . import resources
from . import common

from eng.constants.buttons import *

#contexts
CX_PAUSE = 0
CX_BAG_USEITEM = 1
CX_BAG_GIVEITEM = 2
CX_BATTLE_CHOOSENEW = 3

#party screen states
PS_NORMAL = 0
PS_SWITCH = 1
PS_WAITFORDISAPPEAR = 2
PS_WAITFORAPPEAR = 3

#party box states
PB_NORMAL = 0
PB_SWITCH = 1
PB_DISAPPEAR = 2
PB_APPEAR = 3

#mini menu options
MM_SUMMARY = 0
MM_SWITCH = 1
MM_ITEM = 2
MM_CANCEL = 3
MM_FIELDEFFECT = 4

#directory for fieldmoves
FIELDMOVES = {}

#formatting
MAINBOX_ORIGIN = (17, 50)
SIDEBOX_ORIGIN = (105, 7)

#number of frames a box takes to appear/disappear
SWITCHTIME = 10

#messages
MSG_CHOOSE = "Choose a pokemon."
MSG_MINIMENU = "Do what with this pokemon?"
MSG_MOVE = "Move to where?"

class PartyScreen(interface.Interface):
   """The pokemon party screen."""
   
   def __init__(self, screen, context, game):
      """
      Create the menu and the initial boxes.

      screen - the screen to blit to.
      context - the (context, caller) tuple we've been called from.
      game - the game to show about.
      """

      #init
      fn = resources.getFilename(resources.I_PARTY)
      self.partyNode = data.getTreeRoot(fn, "Party config.")
      fn = self.partyNode.getAttr("back", data.D_FILENAME)
      self.transparency = self.partyNode.getAttr("transparency", data.D_INT3LIST)
      
      self.init(screen, background=fn,
                        transparency=self.transparency)
      
      #store variables for later
      self.context, self.caller = context
      self.game = game
      self.party = game.party

      #create script engine
      self.scriptEngine = script_engine.ScriptEngine()

      #font
      fn = self.partyNode.getAttr("font", data.D_FILENAME)
      self.font = font.Font(fn)
      fn = self.partyNode.getAttr("boxfont", data.D_FILENAME)
      self.boxFont = font.Font(fn)      

      #create boxes list
      self.boxes = []

      #create the main box using the first poke in the party
      b = self.createBox(0)
      self.boxes.append(b)
      
      #create boxes for each member of the party
      self.sideboxHeight = 0
      for i in range(1, len(self.party)):
         b = self.createBox(i)
         self.boxes.append(b)
         self.sideboxHeight = b.height+1 #so subsequent calls will know how far apart the boxes are

      #create empty boxes for any unused slots
      for i in range(len(self.party), 6):
         b = EmptyBox(self, self.partyNode)
         self.addWidget(b, (SIDEBOX_ORIGIN[0], SIDEBOX_ORIGIN[1]+(self.sideboxHeight*(i-1))))
         self.boxes.append(b)
         self.sideboxHeight = b.height+1

      #create message
      self.message = interface.Message(self, MSG_CHOOSE, resources.BOXPATH, width=((self.width*2)/3),
                                                                                     padding=4)
      self.message.setPosition((0, self.height), interface.SW)
      self.addWidget(self.message)
         

      #start with the first pokemon
      self.current = 0
      self.currentBox = None
      self.giveFocus(self.boxes[self.current])

      self.miniMenu = None
      self.foregroundObject = None

      #start it normal state
      #init switchFrom
      self.status = PS_NORMAL
      self.switchFrom = 0

   def createBox(self, i):
      if i == 0:
         b = MainBox(self, self.partyNode, self.party[0], font=self.boxFont)
         self.addWidget(b, (17,50))
         return b

      else:
         b = SideBox(self, self.partyNode, self.party[i], font=self.boxFont)
         pos = (SIDEBOX_ORIGIN[0],
                SIDEBOX_ORIGIN[1]+(self.sideboxHeight*(i-1)))
         self.addWidget(b, pos)
         return b

   def runScript(self, s):
      """
      Have the script engine run a script.

      s - the script to run.
      """

      #run the script, with self as caller
      self.scriptEngine.run(s, self)

   def onInputButton(self, button):
      """
      Process a button press.

      button - the button which was pressed.
      """

      #if we have a foreground object, send the button to that
      if self.foregroundObject is not None:
         self.foregroundObject.inputButton(button)
         return

      #else if we're sending input to a widget, send it on
      if self.miniMenu is not None:
         if self.miniMenu.busy:
            self.miniMenu.onInputButton(button)
            return
         else:
            self.miniMenu = None

      #otherwise process it ourselves

      #if we're in normal state:
      #A should open a minimenu
      #B should quit
      #arrows should move the focus
      if self.status == PS_NORMAL:
            if button == BT_A:
               if self.context == CX_PAUSE:
                  self.miniMenu = self.createMiniMenu(self.party[self.current])
                  self.miniMenu.setPosition((self.width-4, self.height-4), interface.SE)
                  self.addWidget(self.miniMenu)
                  self.message.text = MSG_MINIMENU
               elif self.context == CX_BAG_USEITEM:
                  self.party[self.current].useItemOn(self.context[1].getSelectedItem())
                  self.context[1].decreaseSelectedItem()
                  self.context[1].miniMenu.destroy()
                  self.busy = False
               elif self.context == CX_BAG_GIVEITEM:
                  poke = self.party[self.current]
                  oldItem = poke.heldItem
                  poke.heldItem = self.context[1].getSelectedItem()
                  self.context[1].decreaseSelectedItem()
                  print("Gave %s the %s" % (poke.getName(), poke.heldItem.name))
                  if oldItem is not None:
                     self.context[1].bag.add(oldItem)
                     self.context[1].pocket.updateLists()
                     print("Recieved %s from %s and put in bag" % (poke.getName(), oldItem.name))
                  self.context[1].miniMenu.destroy()
                  self.busy = False
            elif button == BT_B:
               self.busy = False
            elif button == BT_UP:
               if self.current > 1:
                  self.current -= 1
                  self.giveFocus(self.boxes[self.current])
            elif button == BT_DOWN:
               if self.current < len(self.party)-1:
                  self.current += 1
                  self.giveFocus(self.boxes[self.current])
            elif button == BT_LEFT:
               self.current = 0
               self.giveFocus(self.boxes[self.current])
            elif button == BT_RIGHT:
               if (self.current == 0) and (len(self.party) > 1):
                  self.current = 1
                  self.giveFocus(self.boxes[self.current])

      #if we're waiting for a switch:
      #A should start the switch
      #B should cancel the switch, going back to the minimenu
      #arrows should change the switch target
      elif self.status == PS_SWITCH:
            if button == BT_A:
               self.doSwitch()
            elif button == BT_B:
               self.boxes[self.current].status = PB_NORMAL
               self.boxes[self.switchFrom].status = PB_NORMAL
               self.status = PS_NORMAL
               self.message.text = MSG_CHOOSE
            elif button == BT_UP:
               if self.current > 1:
                  self.boxes[self.current].status = PB_NORMAL
                  self.current -= 1
                  self.boxes[self.current].status = PB_SWITCH
            elif button == BT_DOWN:
               if self.current < len(self.party)-1:
                  self.boxes[self.current].status = PB_NORMAL
                  self.current += 1
                  self.boxes[self.current].status = PB_SWITCH
            elif button == BT_LEFT:
               self.boxes[self.current].status = PB_NORMAL
               self.current = 0
               self.boxes[self.current].status = PB_SWITCH
            elif button == BT_RIGHT:
               if (self.current == 0) and (len(self.party) > 1):
                  self.boxes[self.current].status = PB_NORMAL
                  self.current = 1
                  self.boxes[self.current].status = PB_SWITCH

            #if after processing we're still waiting for the switch,
            #make sure the first poke is highlighted
            if self.status == PS_SWITCH:
               self.boxes[self.switchFrom].status = PB_SWITCH

   def createMiniMenu(self, poke):
      #list field effects
      if len(FIELDMOVES) == 0:
         root = data.getTreeRoot(globs.FIELDEFFECTS, "Field effects global.")
         for effectNode in root.getChildren("fieldeffect"):
            scriptNode = effectNode.getChild("script")
            FIELDMOVES[effectNode.getAttr("id", data.D_STRING)] = script_engine.scriptFromNode(scriptNode)

      #work out what choices we have
      choices = []
      for m in FIELDMOVES:
         for move in poke.moves:
            if move is not None:
               if move.moveId == m:
                  choices.append((move.name, (MM_FIELDEFFECT, FIELDMOVES[m])))
                  break
      choices.append(("Summary", (MM_SUMMARY,)))
      choices.append(("Switch", (MM_SWITCH,)))
      choices.append(("Item", (MM_ITEM,)))
      choices.append(("Cancel", (MM_CANCEL,)))

      return interface.MiniMenu(self, choices, resources.BOXPATH, callback=self.miniMenuChoose,
                                                                  border=7)

   def miniMenuChoose(self, arg):
      choice = arg[0]

      if choice == MM_SUMMARY:
         #create the screen and set it as the foreground object
         self.foregroundObject = summary_screen.SummaryScreen(self._screen, (summary_screen.CX_PARTY, self), self.game, self.current)

      elif choice == MM_SWITCH:
         self.startSwitch()

      elif choice == MM_CANCEL:
         self.miniMenu.destroy()
         self.message.text = MSG_CHOOSE

      elif choice == MM_FIELDEFFECT:
         script = arg[1]
         self.runScript(script)

   def onTick(self):
      if self.status == PS_WAITFORDISAPPEAR:
         if self.boxes[self.switchFrom].counter > SWITCHTIME:
            self.party.switch(self.switchFrom, self.current)

            switchBox = self.createBox(self.switchFrom)
            currentBox = self.createBox(self.current)

            self.boxes[self.switchFrom] = switchBox
            self.boxes[self.current] = currentBox
            
            switchBox.appear()
            currentBox.appear()

            self.giveFocus(self.boxes[self.current])

            self.status = PS_WAITFORAPPEAR
      
      #if we're waiting for the boxes to appear, check whether they've finished appearing (both will do it together)
      #if so, we're done waiting and can go back to normal
      elif self.status == PS_WAITFORAPPEAR:
         if self.boxes[self.switchFrom].status == PB_NORMAL:
            self.status = PS_NORMAL
            self.message.text = MSG_CHOOSE

   def giveFocus(self, box):
      if self.currentBox is not None:
         self.currentBox.selected = False

      box.selected = True
      self.currentBox = box

   def startSwitch(self):
      """Start the switch procedure, looking for a second pokemon."""

      #hide the minimenu and take back input control from it
      self.miniMenu.destroy()
      self.message.text = MSG_MOVE

      #store the current selection as the first pokemon to switch
      #set it's status to switch so it highlights
      self.switchFrom = self.current
      self.boxes[self.switchFrom].status = PB_SWITCH

      #set ourself to switch status
      self.status = PS_SWITCH

   def doSwitch(self):
      """Perform the switch."""
      
      #if they're on the original pokemon, no switch and go back to minimenu
      if self.switchFrom == self.current:
         self.boxes[self.current].status = PB_NORMAL
         self.status = PS_NORMAL

      #otherwise have the two relevant boxes disappear and start waiting for them to do so
      else:
         self.boxes[self.current].disappear()
         self.boxes[self.switchFrom].disappear()
         self.status = PS_WAITFORDISAPPEAR
      

class PartyBox(interface.Widget):
   """Base class for the individual pokemon boxes on the party screen."""
   
   def __init__(self, parent, partyNode, poke, **kwargs):
      """
      Store information and create the icon.

      parent - the parent widget.
      partyNode - the <party> menu node.
      poke - the pokemon this box is relevant to.
      """

      #init base widget
      self.init(parent, **kwargs)

      #store variables we'll need later
      self.poke = poke
      self.speciesNode = poke.speciesNode

      #create the icon
      graphicsNode = self.speciesNode.getChild("graphics")
      iconNode = graphicsNode.getChild("icon")
      fn = iconNode.getAttr("file", data.D_FILENAME)
      self.icon = interface.AnimatedImage(self, fn, 2, ticksPerFrame=10,
                                                       transparency=self.transparency)
      self.addWidget(self.icon, (0,0))
      
      #load the hp bar
      fn = partyNode.getAttr("hpbar", data.D_FILENAME)
      self.hpBar = common.HpBar(self, poke.stats[pokemon.ST_HP], value=poke.currentHP,
                                                                 background=fn,
                                                                 transparency=self.transparency,
                                                                 z=-1)

      #create labels
      self.nameLabel = interface.Label(self, poke.getName())
      self.lvlLabel = interface.Label(self, "Lv%s" % poke.level)
      self.hpLabel = interface.Label(self, "%i/%i" % (poke.currentHP, poke.stats[pokemon.ST_HP]))

      #load item icon
      fn = partyNode.getAttr("item", data.D_FILENAME)
      self.itemIcon = interface.Image(self, fn, transparency=self.transparency)
      
      self._status = PB_NORMAL
      self.counter = 0
      self._selected = False

   @property
   def selected(self):
      return self._selected

   @selected.setter
   def selected(self, val):
      self._selected = val
      self.selectedBox.visible = self._selected

   @property
   def status(self):
      return self._status

   @status.setter
   def status(self, val):
      self._status = val
      if val == PB_NORMAL:
         self.switchBox.visible = False
      else:
         self.switchBox.visible = True

   def disappear(self):
      self.status = PB_DISAPPEAR
      self.counter = 0
      self.basePosition = self.position

class MainBox(PartyBox):
   def __init__(self, parent, partyNode, poke, **kwargs):
      mainNode = partyNode.getChild("main")
      fn = mainNode.getAttr("file", data.D_FILENAME)
      self.transparency = partyNode.getAttr("transparency", data.D_INT3LIST)
      
      PartyBox.__init__(self, parent, partyNode, poke, background=fn,
                                                       transparency=self.transparency,
                                                       **kwargs)

      self.border = 3
      self.lineBuffer = 1

      fn = mainNode.getAttr("selected", data.D_FILENAME)
      self.selectedBox = interface.Image(self, fn, transparency=self.transparency)
      self.addWidget(self.selectedBox, (0,0))
      self.selectedBox.visible = False

      fn = mainNode.getAttr("switch", data.D_FILENAME)
      self.switchBox = interface.Image(self, fn, transparency=self.transparency,
                                                 z=-1)
      self.addWidget(self.switchBox, (0,0))
      self.switchBox.visible = False
      
      self.addWidget(self.nameLabel, (32+self.border, self.border))

      pos = (self.nameLabel.position[0],
             self.nameLabel.position[1]+self.nameLabel.height+self.lineBuffer)
      self.addWidget(self.lvlLabel, pos)

      pos = (self.width-self.border,
             self.lvlLabel.position[1]+self.lvlLabel.height+self.lineBuffer)
      self.addWidget(self.hpBar, pos, anchor=interface.NE)

      pos = (self.width-self.border,
             self.hpBar.position[1]+self.hpBar.height+self.lineBuffer)
      self.addWidget(self.hpLabel, pos, anchor=interface.NE)

   def appear(self):
      self.status = PB_APPEAR
      self.counter = 0
      self.basePosition = self.position

      distance = self.basePosition[0]+self.width
      self.position = (self.basePosition[0]-distance, self.basePosition[1])

   def onTick(self):
      self.counter += 1
      if self.counter >= 600:
         self.counter = 0

      if self.status == PB_DISAPPEAR:
         distance = self.x+self.width
         offset = (distance*self.counter)/SWITCHTIME
         self.position = (self.basePosition[0]-offset, self.basePosition[1])
         
         if self.counter > SWITCHTIME:
            self.destroy()

      elif self.status == PB_APPEAR:
         distance = self.basePosition[0]+self.width
         offset = (distance*(SWITCHTIME-self.counter))/SWITCHTIME
         self.position = (self.basePosition[0]-offset, self.basePosition[1])
         
         if self.counter > SWITCHTIME:
            self.position = self.basePosition
            self.status = PB_NORMAL
         

class SideBox(PartyBox):
   def __init__(self, parent, partyNode, poke, **kwargs):
      sideNode = partyNode.getChild("side")
      fn = sideNode.getAttr("file", data.D_FILENAME)
      self.transparency = partyNode.getAttr("transparency", data.D_INT3LIST)
      
      PartyBox.__init__(self, parent, partyNode, poke, background=fn,
                                                       transparency=self.transparency,
                                                       **kwargs)

      self.border = 3
      self.lineBuffer = 1

      fn = sideNode.getAttr("selected", data.D_FILENAME)
      self.selectedBox = interface.Image(self, fn, transparency=self.transparency)
      self.addWidget(self.selectedBox, (0,0))
      self.selectedBox.visible = False

      fn = sideNode.getAttr("switch", data.D_FILENAME)
      self.switchBox = interface.Image(self, fn, transparency=self.transparency,
                                                 z=-1)
      self.addWidget(self.switchBox, (0,0))
      self.switchBox.visible = False
      
      self.addWidget(self.nameLabel, (32+self.border, self.border))

      pos = (self.nameLabel.position[0],
             self.nameLabel.position[1]+self.nameLabel.height+self.lineBuffer)
      self.addWidget(self.lvlLabel, pos)

      pos = (self.width-self.border,
             self.border)
      self.addWidget(self.hpBar, pos, anchor=interface.NE)

      pos = (self.width-self.border,
             self.hpBar.position[1]+self.hpBar.height+self.lineBuffer)
      self.addWidget(self.hpLabel, pos, anchor=interface.NE)

   def appear(self):
      self.status = PB_APPEAR
      self.counter = 0
      self.basePosition = self.position
      
      distance = self.parent.width-self.basePosition[0]
      self.position = (self.basePosition[0]+distance, self.basePosition[1])

   def onTick(self):
      self.counter += 1
      if self.counter >= 600:
         self.counter = 0

      if (self.status == PB_DISAPPEAR):
         distance = self.parent.width-self.basePosition[0]
         offset = (distance*self.counter)/SWITCHTIME
         self.position = (self.basePosition[0]+offset, self.basePosition[1])
         
         if self.counter > SWITCHTIME:
            self.destroy()

      elif (self.status == PB_APPEAR):
         distance = self.parent.width-self.basePosition[0]
         offset = (distance*(SWITCHTIME-self.counter))/SWITCHTIME
         self.position = (self.basePosition[0]+offset, self.basePosition[1])
         
         if self.counter > SWITCHTIME:
            self.position = self.basePosition
            self.status = PB_NORMAL

class EmptyBox(interface.Widget):
   def __init__(self, parent, partyNode, **kwargs):
      emptyNode = partyNode.getChild("empty")
      fn = emptyNode.getAttr("file", data.D_FILENAME)
      self.transparency = partyNode.getAttr("transparency", data.D_INT3LIST)
      
      self.init(parent, background=fn,
                        transparency=self.transparency,
                        **kwargs)
         
         
      
      
