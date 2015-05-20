import os

import pygame

import eng.interface as interface
import eng.font as font
import eng.box as box
import eng.tileset as tileset
import eng.data as data
import eng.globs as globs
import eng.items as items
import eng.sound as sound
from . import resources
from . import party_screen

from eng.constants.buttons import *

#mini menu options
MM_USE = 0
MM_GIVE = 1
MM_TOSS = 2
MM_CANCEL = 3

#contexts to be called from
CX_PAUSE = 0
CX_POKEMON_GIVEITEM = 1
CX_BATTLE_USEITEM = 2

class BagScreen(interface.Interface):
   """The bag screen."""
   
   def __init__(self, screen, context, game):
      """
      Create the bag menu.

      screen - the screen to blit to.
      context - the (context constant, caller) tuple.
      game - the game object.
      """

      #init
      fn = resources.getFilename(resources.I_BAG)
      bagNode = data.getTreeRoot(fn, "Bag config.")
      fn = bagNode.getAttr("back", data.D_FILENAME)
      self.transparency = bagNode.getAttr("transparency", data.D_INT3LIST)
      
      self.init(screen, background=fn,
                        transparency=self.transparency)

      #store useful data
      self.context, self.caller = context
      self.game = game
      
      self.bag = self.game.bag

      #load pockets node
      self.pocketsNode = bagNode.getChild("pockets")

      #create font
      self.font = font.Font(bagNode.getAttr("font", data.D_FILENAME))

      #load misc bag icons
      iconsNode = bagNode.getChild("bagicons")
      tsId = iconsNode.getAttr("tileset", data.D_STRING)
      self.iconsTs = tileset.Tileset(tsId)

      #set the current selected item as the first
      self.currentPocket = 0
      self.numPockets = len(self.pocketsNode.getChildren("pocket"))

      #load the first pocket
      self.pocket = None
      self.loadPocket()

      #minimenu
      choices = (("Use", MM_USE),
                 ("Give", MM_GIVE),
                 ("Toss", MM_TOSS),
                 ("Cancel", MM_CANCEL))
      self.miniMenu = interface.MiniMenu(self, choices, resources.BOXPATH, callback=self.miniMenuChoose,
                                                                           border=7)
      self.miniMenu.setPosition(self.size, interface.SE)
      self.addWidget(self.miniMenu)
      self.miniMenu.visible = False

      #play a sound effect
      sound.playEffect(sound.SD_MENUOPEN)

   def getSelectedItem(self):
      return self.pocket.getSelectedItem()

   def decreaseSelectedItem(self, number=1):
      self.pocket.decreaseSelectedItem(number)

   def inputButton(self, button):
      """
      Process a button press.

      button - the button that was pressed.
      """

      
      #if we have a foreground object, send the button to that
      if self.foregroundObject is not None:
         self.foregroundObject.inputButton(button)
         return

      #else if we're sending input to a minimenu, send it on
      if self.miniMenu.visible:
         if self.miniMenu.busy:
            self.miniMenu.onInputButton(button)
            return
         else:
            self.miniMenu.visible = False

      #otherwise process it ourselves
      #if we've been called from the pause menu
      if self.context == CX_PAUSE:
            #if it was A, then if we're on an item show the mini menu, else close
            if button == BT_A:
               if self.pocket.current != self.pocket.numOptions-1:
                  self.miniMenu.visible = True
               else:
                  self.busy = False
            #if it was the B button, exit
            elif button == BT_B:
               self.busy = False
            #left or right should change pockets
            elif button == BT_LEFT:
               if self.currentPocket > 0:
                  self.currentPocket -= 1
                  self.loadPocket()
            elif button == BT_RIGHT:
               if self.currentPocket < self.numPockets-1:
                  self.currentPocket += 1
                  self.loadPocket()
            #feed up or down keys to the pocket widget
            elif button == BT_UP:
               self.pocket.inputButton(BT_UP)
            elif button == BT_DOWN:
               self.pocket.inputButton(BT_DOWN)
                  
      elif self.context == CX_POKEMON_GIVEITEM:
            pokemon = self.caller[1]
            if button == BT_A:
               if self.current != self.itemNums[self.currentPage]:
                  item = self.bagFill[self.currentPage][self.current]
                  if pokemon.heldItem == None:
                     print(pokemon.id + " given " + item.id)
                     pokemon.heldItem = item.id
                     self.bag.remove(item, 1)
                  else:
                     print("the pokemon is already holding an item, they will be swapped")
                     print(pokemon.heldItem + " swapped for " + item.id)
                     # make an actual item of the item the pokemon is holding
                     heldItem = items.Item(pokemon.heldItem)
                     # change the item the pokemon is holding
                     pokemon.heldItem = item.id
                     # remove the held item from the bag and add the item the pokemon was originally holding
                     self.bag.remove(item, 1)
                     self.bag.add(heldItem, 1)
                  self.busy = False
               else:
                  self.busy = False    
            #if it was the B button, exit
            elif button == BT_B:
               self.busy = False
            #left or right should change pages
            elif button == BT_LEFT:
               if self.currentPage > 0:
                  self.currentPage -= 1
                  self.current = 0
                  self.loadPage()
            elif button == BT_RIGHT:
               if self.currentPage < self.pocketsNum -1:
                  self.currentPage += 1
                  self.current = 0
                  self.loadPage()
            elif button == BT_UP:
               if self.current > 0:
                  self.current -= 1
                  self.loadPage()
            elif button == BT_DOWN:
               if self.current < self.itemNums[self.currentPage]:
                  self.current += 1
                  self.loadPage()

   def miniMenuChoose(self, choice):
      print(choice)

   def loadPocket(self):
      """
      Load a new page.

      Based off the currentPage attribute.
      """

      #remove old pocket
      if self.pocket is not None:
         self.pocket.destroy()

      #add new pocket
      self.pocket = PocketWidget(self, self.pocketsNode, self.currentPocket, self.iconsTs, self.bag)
      self.addWidget(self.pocket, (0,0))

class PocketWidget(interface.Widget):
   """Displays the contents of a single pocket."""
   
   def __init__(self, parent, pocketsNode, pocketIndex, iconsTs, bag, **kwargs):
      """
      Create the pocket widget.

      parent - the parent menu.
      pocketsNode - the <pockets> node to use.
      pocketIndex - the index of the pocket to load.
      iconsTs - the icon tileset to use.
      bag - the bag object.
      """      
      
      #init widget
      fn = pocketsNode.getAttr("back", data.D_FILENAME)
      kwargs["background"] = fn
      self.init(parent, **kwargs)

      #load the correct pocket from the bag
      pocketNode = pocketsNode.getChildren("pocket")[pocketIndex]
      pocketId = pocketNode.getAttr("id", data.D_STRING)
      self.pocket = bag.getPocket(pocketId)
      self.numOptions = len(self.pocket)+1
      self.current = 0

      #cursor
      self.cursor = iconsTs[0]

      #print the name of the pocket
      text = pocketNode.getAttr("name", data.D_STRING)
      l = interface.Label(self, text)
      self.addWidget(l, (24,8))

      #draw the image of the bag
      tsId = pocketsNode.getAttr("bagicon", data.D_STRING)
      bagTileset = tileset.Tileset(tsId)
      bagImage = bagTileset[pocketIndex]
      im = interface.Image(self, bagImage)
      self.addWidget(im, (10,34))

      #left and right arrows
      if self.parent.currentPocket > 0:
         im = interface.Image(self, iconsTs[1])
         self.addWidget(im, (0,60))
      if self.parent.currentPocket < self.parent.numPockets-1:
         im = interface.Image(self, iconsTs[2])
         self.addWidget(im, (60,60))

      #create the item bar
      self.itemBar = ItemBar(self, pocketsNode.getChild("itembar"))
      self.itemBar.setPosition((0, self.height), interface.SW)
      self.addWidget(self.itemBar)
      
      self.updateItemBar()
      

   def updateLists(self):
      self.numOptions = len(self.pocket)+1
      self.updateItemBar()

   def updateItemBar(self):
      """
      Update what the item bar shows after a change in selection.

      Based upon the value of self.current
      """

      #try to get the item from the pocket as indexed by self.current
      #if this fails, we must be at the end of the list, so set it to None
      try:
         selectedItem = self.pocket[self.current]
      except IndexError:
         selectedItem = None
      self.itemBar.setItem(selectedItem)

   def getSelectedItem(self):
      try:
         return self.pocket[self.current]
      except IndexError:
         return None

   def decreaseSelectedItem(self, number=1):
      self.pocket.remove(self.pocket[self.current], number)
      self.updateLists()

   def inputButton(self, button):
      """
      Process a button press.

      Note we should only get UP and DOWN presses.

      button - the button that was pressed.
      """

      #up and down should scroll the item list
      if button == BT_UP:
         if self.current > 0:
            self.current -= 1
            self.updateItemBar()
            sound.playEffect(sound.SD_CHOOSE)
      elif button == BT_DOWN:
         if self.current < self.numOptions-1:
            self.current += 1
            self.updateItemBar()
            sound.playEffect(sound.SD_CHOOSE)

   def preDraw(self):
      #write the list of each item
      firstListIndex = max(0, self.current - 5)
      pointerX = self._screenPosition[0]+100
      pointerY = self._screenPosition[1]+12
      for i in range(firstListIndex, min(firstListIndex + 6, self.numOptions)):
         #if it's the final item, write Cancel
         #else write the name and quantity of the item
         if i == self.numOptions-1:
            self.font.writeText("Cancel", self._screen, (self._screenPosition[0]+100, pointerY))
         else:
            item = self.pocket[i]
            amount = "x%i" % self.pocket.getQuantity(item)
            self.font.writeText(item.name, self._screen, (pointerX, pointerY))
            self.font.writeText(amount, self._screen, (pointerX+100, pointerY))

         #draw the cursor
         if i == self.current:
            self._screen.blit(self.cursor, (self._screenPosition[0]+85, pointerY))
         pointerY += 16

class MiniMenu(interface.Widget):
   def __init__(self, parent, location, item):
      base_menu.Widget.__init__(self, parent, location)

      self.item = item

      #create the font
      self.font = font.Font(globs.FONT)

      self.objectBuffer = 2
      self.border = 10
      self.lineBuffer = 3

      #load the side cursor
      dialogFn = os.path.join(globs.DIALOG)
      root = data.getTreeRoot(dialogFn, "Ditto main")
      self.transparency = root.getAttr("transparency", data.D_INT3LIST)
      cursorFn = root.getAttr("sidecursor", data.D_FILENAME)
      self.sideCursor = data.getImage(cursorFn, dialogFn).convert(self.screen)
      self.sideCursor.set_colorkey(self.transparency)

      #work out what choices we have
      self.choices = []
      self.choices.append((MM_USE, "Use"))
      self.choices.append((MM_GIVE, "Give"))
      self.choices.append((MM_TOSS, "Toss"))
      self.choices.append((MM_CANCEL, "Cancel"))
      
      #create a list of the names for each option
      #use to determine the size of the menu
      names = [choice[1] for choice in self.choices]
      self.size = (max(list(map(self.font.calcWidth, names))) + self.border*2 + self.sideCursor.get_width(),
                   (self.border*2)+(self.font.height*len(self.choices))+(self.lineBuffer*(len(self.choices)-1)))

      #create the actual box
      self.box = box.Box(self.size)

      #write each choice onto the box
      i = 0
      for choice in self.choices:
         text = choice[1]
         location = self.border+self.sideCursor.get_width(), (i*(self.font.height+self.lineBuffer))+self.border
         self.font.writeText(text, self.box, location)
         i += 1

      #start with top option
      self.current = 0

      #set busy
      self.busy = True

   def inputButton(self, button):
      if self.parent.foregroundObject is not self.parent.miniMenu:
         if button == BT_A:
            self.choose(self.choices[self.current])
         elif button == BT_B:
            self.destroy()
         elif button == BT_UP:
            if self.current > 0:
               self.current -= 1
         elif button == BT_DOWN:
            if self.current < len(self.choices)-1:
               self.current += 1
      else:
         self.parent.foregroundObject.inputButton(button)

   def choose(self, choice):
      item = self.parent.getSelectedItem()
      # there will need to be additional code added so that if the menu screen is called from the battle screen it can use the item.inbattle options
      if choice[0] == MM_USE:
         if item.outBattle in [1, 3, 4, 5]:
            print("try to use item on pokemon")
            self.parent.foregroundObject = party_screen.PartyScreen(self.screen,
                                                                    self.parent.menuNode,
                                                                    (party_screen.CX_BAG_USEITEM, self.parent),
                                                                    self.parent.game)
         elif item.outBattle == 2:
            print("use item has world affect")
            self.parent.decreaseSelectedItem()
            self.destroy()
         else:
            print("cannot be used out of battle")

      elif choice[0] == MM_GIVE:
         if True:
            print("try to give item to pokemon")
            self.parent.foregroundObject = party_screen.PartyScreen(self.screen,
                                                                    self.parent.menuNode,
                                                                    (party_screen.CX_BAG_GIVEITEM, self.parent),
                                                                    self.parent.game)

      elif choice[0] == MM_TOSS:
         self.parent.decreaseSelectedItem()
         self.destroy()

      elif choice[0] == MM_CANCEL:
         self.destroy()
      
   def draw(self):
      if self.visible:
         self.screen.blit(self.box, self.screenLocation)
         loc = (self.screenLocation[0]+self.border,
                self.screenLocation[1]+self.border+(self.current*(self.font.height+self.lineBuffer)))
         self.screen.blit(self.sideCursor, loc)

         base_menu.Widget.draw(self)

class ItemBar(interface.Widget):
   """Widget to show the item info at the bottom of the screen."""
   
   def __init__(self, parent, itembarNode, **kwargs):
      """
      Create the item bar.

      parent - the parent widget.
      location - the location of the widget relative to its parent.
      font - the font to write with.
      itembarNode - the <itembar> node.
      """

      #init the base widget
      fn = itembarNode.getAttr("back", data.D_FILENAME)
      kwargs["background"] = fn
      self.init(parent, **kwargs)

      #load the back arrow image
      fn = itembarNode.getAttr("backarrow", data.D_FILENAME)
      self.backArrow = data.getImage(fn, itembarNode.ditto_fn)

      #labels
      self.icon = None
      self.labels = []
      
   def setItem(self, item):
      """
      Set the item to display.

      item - the item, or use None for end of list.
      """

      #destroy previous widgets
      if self.icon is not None:
         self.icon.destroy()
         self.icon = None
      for l in self.labels:
         l.destroy()
      self.labels = []

      #the item's picture
      #if None, draw the back arrow
      if item is not None:
         surf = item.getImage()
      else:
         surf = self.backArrow
      im = interface.Image(self, surf)
      self.addWidget(im, (8,12))
      self.icon = im
         
      #write the item's description
      #if None, write relevant text
      if item is not None:
         descriptionLines = self.splitDescription(item.description)
      else:
         descriptionLines = ["","Close bag"] #TODO - maybe get text from node?
         
      pointerY = 4      
      for line in descriptionLines:
         l = interface.Label(self, line, colour="white")
         self.addWidget(l, (40,pointerY))
         self.labels.append(l)
         pointerY += self.font.height+1

   def splitDescription(self, description):
      """
      Split up the description into a list of lines of the correct width.

      description - the description to split up.
      """
      #TODO - maybe move out of class to a module function?
      
      box_width = 196 #TODO - make a formatting constant
      
      # first split up description into words
      word = ""
      words = []
      for char in description:
         if char != " ":
            word += char
         elif char == " ":
            words.append(word)
            word = ""
      else:
         words.append(word)

      # then figure out how long each word is (in pixels)
      word_lens = []
      for word in words:
         word_lens.append(self.font.calcWidth(word))
      space_len = self.font.calcWidth(" ")

      # iterate through the words adding them until they get too long, then send them to sentance and repeat til all words are done
      s_length = 0   # length of currently being formed line
      num_words = len(words)
      lines = []
      sentance = ""
      for curr in range(0,  num_words):
         curr_length = word_lens[curr]
         if s_length + curr_length + space_len <= box_width:
            sentance = sentance + words[curr] + " "
            s_length += curr_length + space_len
         else:
            lines.append(sentance)
            s_length = curr_length + space_len
            sentance = words[curr] + " "
      lines.append(sentance)
      return lines
         
