import os

import pygame

import eng.interface as interface
import eng.data as data
import eng.font as font
from . import resources

from eng.constants.buttons import *

CX_BAG_USEITEM = 0
CX_PARTY_FLY = 1

class MapScreen(interface.Interface):
   """The map screen"""
   
   def __init__(self, screen, context, game):
      """
      Create the map screen

      screen - the screen to blit to.
      context - a tuple of (context constant, caller).
      game - the current game.
      """

      #init
      mapNode = data.getTreeRoot(resources.getFilename(resources.I_MAP), "Menu config.")
      fn = mapNode.getAttr("back", data.D_FILENAME)
      self.transparency = mapNode.getAttr("transparency", data.D_INT3LIST)      
      self.init(screen, context, background=fn,
                                 transparency=self.transparency)

      #load town map data file
      dataNode = mapNode.getChild("data")
      fn = dataNode.getAttr("file", data.D_FILENAME)
      townmapRoot = data.getTreeRoot(fn)

      #store grid and map sizes
      #maybe calculate map size from image size and grid size?
      self.gridSize = townmapRoot.getAttr("grid", data.D_INT2LIST) #tuple size of a single grid square
      self.mapSize = townmapRoot.getAttr("size", data.D_INT2LIST) #tuple number of grid squares on the map. 

      #set the font
      fn = mapNode.getAttr("font", data.D_FILENAME)
      self.font = font.Font(fn)

      #load the icons
      iconsNode = mapNode.getChild("icons")
      flyIconFn = iconsNode.getAttr("fly", data.D_FILENAME)

      #dictionaries for location info
      self.locations = {}      #{position: (map name, map id)}
      self.sublocations = {}   #{position: (location name, map id)}
      self.flyData = {}        #{position: target map filename}

      #iterate through each location, adding data to the dicts
      self.currLocation = self.mapSize[0]/2, self.mapSize[1]/2 #default centre of the map
      foundPlayer = False
      for locationNode in townmapRoot.getChildren("location"):
         position = tuple(locationNode.getAttr("position", data.D_INT2LIST))
         mapId = locationNode.getAttr("id", data.D_STRING)
         name = locationNode.getAttr("name", data.D_STRING)
         mapFn = locationNode.getOptionalAttr("file", data.D_STRING)

         self.locations[position] = (name, mapId)

         #if we're given a flight destination, store it
         #and if we're trying to fly, add the icon on the map
         if mapFn is not None:
            self.flyData[position] = mapFn

            if self.context == CX_PARTY_FLY:
               anim = interface.AnimatedImage(self, flyIconFn, 2, ticksPerFrame=12,
                                                                  transparency=self.transparency,
                                                                  z=1)
               self.addWidget(anim, self.pixelLoc(position, anim.size))

         #if the id of the map matches the current game map's id, then set the current location
         if mapId == game.player.map.id:
            self.currLocation = position
            foundPlayer = True
            
      #also iterate through the sublocations to populate that dict
      for sublocationNode in townmapRoot.getChildren("sublocation"):
         position = tuple(sublocationNode.getAttr("position", data.D_INT2LIST))
         mapId = sublocationNode.getAttr("id", data.D_STRING)
         name = sublocationNode.getAttr("name", data.D_STRING)

         self.sublocations[position] = (name, mapId)

      #if we found the player, add the icon to the map
      if foundPlayer:
         fn = iconsNode.getAttr("player", data.D_FILENAME)
         self.im = interface.Image(self, fn, transparency=self.transparency)
         pos = self.pixelLoc(self.currLocation, self.im.size)
         self.addWidget(self.im, pos)

      #create selection cursor
      #if we found the player it'll start where they are, else centre of map
      fn = iconsNode.getAttr("selection", data.D_FILENAME)
      self.select = SelectionCursor(self, fn, self.gridSize, transparency=self.transparency,
                                                                          ticksPerFrame=10,
                                                                          z=2)
      self.addWidget(self.select, (0,0))
      self.select.gridPosition = self.currLocation

      #create the name box
      #work out what the maximum width of a name that could be shown would be
      #the box draws with our font, so it will be accurate
      #set it up with the right text
      names = [a[0] for a in (list(self.locations.values())+list(self.sublocations.values()))]
      maxWidth = max(list(map(self.font.calcWidth, names)))
      self.box = NameBox(self, maxWidth)
      self.addWidget(self.box, (0,0))
      self.updateNameBox()

   def updateNameBox(self):
      """Update the name box text and visiblity based on current location."""

      #if we're currently on a location, get the name and map id
      try:
         name, mapId = self.locations[self.currLocation]

      #if not, then set the text and subtext to empty, and hide the box
      #then return as we're done
      except KeyError:
         self.box.text = ""
         self.box.subText = ""
         self.box.visible = False
         return

      #if it worked, then make it show the name, and make sure it's visible
      self.box.text = name
      self.box.visible = True

      #if there's a sublocation, get it's name and mapId
      try:
         name, mapId = self.sublocations[self.currLocation]

      #if not, then set the subtext to empty
      #then return 
      except KeyError:
         self.box.subText = ""
         return

      #if there was a sublocation, make to box show it
      self.box.subText = name

   def pixelLoc(self, gridLocation, imSize=None):
      """
      Determine the pixel co-ordinate to place on image at so it is centred at the given grid location.

      gridLocation - the grid coordinate.
      imSize - the size of the image, defaults to the grid size.
      """

      #if no im size given, use the grid size
      if imSize is None:
         imSize = self.gridSize

      #calculate the offset required to centre the image
      offset = ((self.gridSize[0]-imSize[0])/2,
                (self.gridSize[1]-imSize[1])/2)

      #return the pizel coordinate
      return ((self.gridSize[0]*gridLocation[0])+offset[0],
              (self.gridSize[1]*gridLocation[1])+offset[1])

   def inputButton(self, button):
      """
      Process a button press.

      button - the button that was pressed.
      """

      #if it's A, and we can fly to the currently selected position, do so
      if button == BT_A:         
         if self.context == CX_PARTY_FLY and self.currLocation in self.flyData:
            self.quitAll()
            #fly

      #if it was the B button, exit
      if button == BT_B:
         self.busy = False

   def onTick(self):
      """Update the selection cursor based on keydowns."""

      #if left is being held down, try to move left
      #if we have space to move into, then ask the cursor to move left
      #take the current location of the cursor, and update the name box accordingly
      if BT_LEFT in self.keysDown:
         if self.currLocation[0] > 0:
            self.select.moveLeft()
            self.currLocation = self.select.gridPosition
            self.updateNameBox()

      #similarly for the other directions      
      if BT_RIGHT in self.keysDown:
         if self.currLocation[0] < self.mapSize[0] - 1:
            self.select.moveRight()
            self.currLocation = self.select.gridPosition
            self.updateNameBox()
      if BT_UP in self.keysDown:
         if self.currLocation[1] > 0:
            self.select.moveUp()
            self.currLocation = self.select.gridPosition
            self.updateNameBox()
      if BT_DOWN in self.keysDown:
         if self.currLocation[1] < self.mapSize[1] - 1:
            self.select.moveDown()
            self.currLocation = self.select.gridPosition
            self.updateNameBox()

#name box spacer
SPACER = 2

class NameBox(interface.Widget):
   """
   Box to show map names and sublocations.

   Changes size depending whether the subtext is an empty string or not.
   """
   
   def __init__(self, parent, maxTextWidth, **kwargs):
      """
      Init the box.

      parent - the parent widget.
      maxTextWidth - the width of the longest name we'll have to show.
      """

      #init the widget
      self.init(parent, **kwargs)

      #create the small surface for when there's no subtext
      self.smallSurface = pygame.Surface((maxTextWidth+(SPACER*2), self.font.height+(SPACER*2)))
      self.smallSurface.fill((150,150,150))
      self.smallSurface.set_alpha(200)

      #create the large surface for when there is a subtext
      self.bigSurface = pygame.Surface((maxTextWidth+(SPACER*2), (self.font.height*2)+(SPACER*3)))
      self.bigSurface.fill((150,150,150))
      self.bigSurface.set_alpha(200)

      #label for the main text
      self.label = interface.Label(self, colour="white")
      self.addWidget(self.label, (SPACER,SPACER))

      #label for the subtext
      self.subLabel = interface.Label(self, colour="white")
      self.addWidget(self.subLabel, (SPACER, self.font.height+(SPACER*2)))

      #initialise text and subtext as empty strings
      self._text = ""
      self._subText = ""

   @property
   def text(self):
      """Getter for text property."""
      
      return self._text

   @text.setter
   def text(self, val):
      """Setter for text property."""

      #set text and update the label
      self._text = val
      self.label.text = val

   @property
   def subText(self):
      """Getter for subText property."""
      
      return self._subText

   @subText.setter
   def subText(self, val):
      """Setter for subText property."""

      #set the subtext and update the label
      self._subText = val
      self.subLabel.text = val

   def preDraw(self):
      """Draw the surface behind the labels."""

      #if there's no subtext, use the small surface
      #if there is, use the big one
      if self.subText == "":
         self._screen.blit(self.smallSurface, self._screenPosition)
      else:
         self._screen.blit(self.bigSurface, self._screenPosition)

class SelectionCursor(interface.Widget):
   """Cursor to show the current selection."""
   
   def __init__(self, parent, fn, gridSize, **kwargs):
      """
      Init the cursor.

      parent - the parent widget.
      fn - path to the cursor animation strip.
      grid size - the size of the map grid.
      """

      #init the widget
      self.init(parent, **kwargs)

      #create the cursor image
      self.image = interface.AnimatedImage(self, fn, 2, **kwargs)
      self.addWidget(self.image, (0,0))

      #calculate image offset
      self.gridSize = gridSize
      self.imageOffset = ((gridSize[0]-self.image.size[0])/2,
                          (gridSize[1]-self.image.size[1])/2)

      #initial grid position
      self._gridPosition = (0,0)

      #not moving yet
      self.moveOffset = (0,0)
      self.offsetList = []
      self.moving = False

   @property
   def gridPosition(self):
      """Getter for gridPosition property."""
      
      return self._gridPosition

   @gridPosition.setter
   def gridPosition(self, val):
      """Setter for gridPosition property."""

      #store new grid position and calculate new position
      self._gridPosition = val
      self.calcNewPosition()

   def calcNewPosition(self):
      """Calculate the widget position depending on the current grid position and offsets."""

      #work out the pixel coordinate and apply offsets
      self.position = ((self.gridPosition[0]*self.gridSize[0])+self.imageOffset[0]+self.moveOffset[0],
                       (self.gridPosition[1]*self.gridSize[1])+self.imageOffset[1]+self.moveOffset[1])

   def moveLeft(self):
      """
      Ask the cursor to move left.

      Ignored if already moving.
      """

      #if we're not already moving, then move the grid position to the left
      #set moving to true, and use offsets to smoothen the movement
      if not self.moving:
         self.gridPosition = (self.gridPosition[0]-1, self.gridPosition[1])
         self.moving = True
         self.offsetList = [((self.gridSize[0]*1)/4, 0),
                            ((self.gridSize[0]*2)/4, 0),
                            ((self.gridSize[0]*3)/4, 0)] #this one gets used first as pop() takes the last value

   def moveRight(self):
      """
      Ask the cursor to move right.

      Ignored if already moving.
      """

      #if we're not already moving, then move the grid position to the right
      #set moving to true, and use offsets to smoothen the movement
      if not self.moving:
         self.gridPosition = (self.gridPosition[0]+1, self.gridPosition[1])
         self.moving = True
         self.offsetList = [((self.gridSize[0]*-1)/4, 0),
                            ((self.gridSize[0]*-2)/4, 0),
                            ((self.gridSize[0]*-3)/4, 0)]

   def moveUp(self):
      """
      Ask the cursor to move up.

      Ignored if already moving.
      """

      #if we're not already moving, then move the grid position up
      #set moving to true, and use offsets to smoothen the movement
      if not self.moving:
         self.gridPosition = (self.gridPosition[0], self.gridPosition[1]-1)
         self.moving = True
         self.offsetList = [(0, (self.gridSize[1]*1)/4),
                            (0, (self.gridSize[1]*2)/4),
                            (0, (self.gridSize[1]*3)/4)]

   def moveDown(self):
      """
      Ask the cursor to move down.

      Ignored if already moving.
      """

      #if we're not already moving, then move the grid position down
      #set moving to true, and use offsets to smoothen the movement
      if not self.moving:
         self.gridPosition = (self.gridPosition[0], self.gridPosition[1]+1)
         self.moving = True
         self.offsetList = [(0, (self.gridSize[1]*-1)/4),
                            (0, (self.gridSize[1]*-2)/4),
                            (0, (self.gridSize[1]*-3)/4)]

   def onTick(self):
      """Update the cursor for one tick."""

      #if we're moving, then if we have any offsets remaining, get the new offset for this frame
      #if we're out of offsets, then set us to have no offset, and we're no longer moving
      #either way, calculate the new position afterwards
      if self.moving:
         if self.offsetList:
            self.moveOffset = self.offsetList.pop()
         else:
            self.moveOffset = (0,0)
            self.moving = False
         self.calcNewPosition()
                            











      
