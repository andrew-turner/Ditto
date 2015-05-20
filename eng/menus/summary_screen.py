import os

import pygame

import eng.interface as interface
import eng.font as font
import eng.tileset as tileset
import eng.data as data
import eng.globs as globs
from . import resources

from eng.constants.stats import *
from eng.constants.buttons import *

#NOTE
#for now everything is placed where it needs to go in the code
#once this screen is finished they all need moving up to constants

CX_PARTY = 0

class SummaryScreen(interface.Interface):
   """The pokemon summary screen object."""
   
   def __init__(self, screen, context, game, startPoke):
      """
      Create the summary screen, starting on the info page of the requested pokemon.

      screen - the surface to blit to.
      context
      game
      startPoke - the index of the pokemon to show first.
      """

      #init
      fn = resources.getFilename(resources.I_SUMMARY)
      self.summaryNode = data.getTreeRoot(fn, "Summary config.")
      fn = self.summaryNode.getAttr("back", data.D_FILENAME)
      self.transparency = self.summaryNode.getAttr("transparency", data.D_INT3LIST)
      
      self.init(screen, background=fn,
                        transparency=self.transparency)

      #store variables for later
      self.context, self.caller = context
      self.party = game.party

      #title font is used in the main box
      self.font = font.Font(self.summaryNode.getAttr("font", data.D_FILENAME))

      #set what to show first - the summary page of the requested pokemon
      self.currentPoke = startPoke
      self.mainBox = None
      self.currentPage = 0
      self.page = None

      #load the pokemon and then the page
      #based off the currentPoke and currentPage attributes
      self.loadPokemon()
      self.loadPage()

   def loadPokemon(self):
      """
      Load the current pokemon, and create the main pokemon box common to all pages.
      """

      #remove old box
      if self.mainBox is not None:
         self.mainBox.destroy()

      #get the required pokemon
      self.poke = self.party[self.currentPoke]

      #create the main box
      mainNode = self.summaryNode.getChild("main")
      self.mainBox = MainBox(self, mainNode, self.poke, z=1)
      self.addWidget(self.mainBox, (2,18))
      
   def loadPage(self):
      """
      Load a new page.

      Based off the currentPage attribute.
      """

      #remove old page
      if self.page is not None:
         self.page.destroy()

      #create the required page 
      if self.currentPage == 0:
         self.page = InfoPage(self, self.summaryNode.getChild("info"), self.poke)
      elif self.currentPage == 1:
         self.page = SkillsPage(self, self.summaryNode.getChild("skills"), self.poke)
      elif self.currentPage == 2:
         self.page = MovesPage(self, self.summaryNode.getChild("moves"), self.poke)

      #add new page
      self.addWidget(self.page, (0,0))

   def inputButton(self, button):
      """
      Process a button press.

      button - the button that was pressed.
      """

      #if it's the B button, we're done
      if button == BT_B:
         self.busy = False

      #left or right should change pages
      elif button == BT_LEFT:
         if self.currentPage > 0:
            self.currentPage -= 1
            self.loadPage()
      elif button == BT_RIGHT:
         if self.currentPage < 2:
            self.currentPage += 1
            self.loadPage()

      #up and down should change pokemon (and therefore reload pages)
      elif button == BT_UP:
         if self.currentPoke > 0:
            self.currentPoke -= 1
            self.loadPokemon()
            self.loadPage()
      elif button == BT_DOWN:
         if self.currentPoke < len(self.party)-1:
            self.currentPoke += 1
            self.loadPokemon()
            self.loadPage()

class MainBox(interface.Widget):
   
   def __init__(self, parent, mainNode, poke, **kwargs):      
      #init
      fn = mainNode.getAttr("back", data.D_FILENAME)
      kwargs["background"] = fn
      self.init(parent, **kwargs)

      #add labels
      l = interface.Label(self, "Lv%i" % poke.level, colour="white")
      self.addWidget(l, (3,3))

      l = interface.Label(self, poke.getName(), colour="white")
      l.setPosition((self.width/2,3), interface.N)
      self.addWidget(l)

      #add battler
      im = interface.Image(self, poke.getBattler())
      im.setPosition((self.width/2, self.height), interface.S)
      self.addWidget(im)

      #TODO
      #status

      #draw the pokeball
      pokeballsNode = mainNode.getChild("pokeballs")
      #create the tileset of pokeballs
      tilesetPath = pokeballsNode.getAttr("tileset", data.D_STRING)
      pokeballPath = pokeballsNode.getAttr("file", data.D_FILENAME)
      pbRoot = data.getTreeRoot(pokeballPath)
      for ballNode in pbRoot.getChildren():
         ballId = ballNode.getAttr("id", data.D_STRING)
         if poke.ballCaughtIn == ballId:
            pbNode = ballNode
            break
      else:
         print(poke.ballCaughtIn)
      i = pbNode.getAttr("index", data.D_INT)
      tileIndex = 2*(i-1)
      ts = tileset.Tileset(tilesetPath)
      pbImage = ts.tiles[tileIndex]
      im = interface.Image(self, pbImage)
      im.setPosition((8, self.height-8), interface.SW)
      self.addWidget(im)

      #draw the shiny star
      if poke.shiny:
         shinyNode = mainNode.getChild("shiny")
         fn = shinyNode.getAttr("file", data.D_FILENAME)
         star = interface.Image(self, fn)
         star.setPosition((self.width-8, self.height-8), interface.SE)
         self.addWidget(star)

class InfoPage(interface.Widget):
   """The info page of the pokemon screen."""

   def __init__(self, parent, infoNode, poke, **kwargs):
      """
      Create the page.

      parent
      infoNode - the <info> node from the menu XML file.
      poke - the pokemon.
      """

      #init widget
      fn = infoNode.getAttr("back", data.D_FILENAME)
      kwargs["background"] = fn
      interface.Widget.init(self, parent, **kwargs)

      #write the page title
      l = interface.Label(self, infoNode.getAttr("title", data.D_STRING))
      self.addWidget(l, (5,2))

      #write all info onto the page 
      info = (poke.speciesNode.getAttr("dex", data.D_STRING),
              poke.getName(),
              "",
              str(poke.trainer),
              str(poke.trainerID),
              ("" if poke.heldItem is None else str(poke.heldItem.name)))
      pointerY = 22
      pointerX = 190
      for inf in info:
         l = interface.Label(self, inf)
         self.addWidget(l, (pointerX, pointerY))
         pointerY += 16

      #nature
      l = interface.Label(self, "%s nature." % poke.getNatureName())
      self.addWidget(l, (8, 136))

      #types
      typesRoot = data.getTreeRoot(globs.TYPES, "Types global")
      
      fn = typesRoot.getAttr("tileset", data.D_STRING)
      typesTs = tileset.Tileset(fn)

      pokeTypes = [poke.type1]
      if poke.type2 is not None:
         pokeTypes.append(poke.type2)

      pointerX = 191
      pointerY = 53
      for t in pokeTypes:
         for typeNode in typesRoot.getChildren("type"):
            if typeNode.getAttr("id", data.D_STRING) == t:
               reqTile = typesTs[typeNode.getAttr("index", data.D_INT)-1]
               im = interface.Image(self, reqTile)
               self.addWidget(im, (pointerX, pointerY))
               pointerX += typesTs.tileSize[0]
               break
         else:
            raise ValueError

class SkillsPage(interface.Widget):
   """The stats page of the pokemon screen."""
   
   def __init__(self, parent, skillsNode, poke, **kwargs):
      """
      Create the page

      parent
      skillsNode - the <skills> node from the menu XML file.
      poke - the pokemon.
      """

      #init widget
      fn = skillsNode.getAttr("back", data.D_FILENAME)
      kwargs["background"] = fn
      interface.Widget.init(self, parent, **kwargs)

      #write the page title
      l = interface.Label(self, skillsNode.getAttr("title", data.D_STRING))
      self.addWidget(l, (5,2))

      #write the poke's hp
      text = "%i/%i" % (poke.currentHP, poke.stats[ST_HP])
      l = interface.Label(self, text)
      l.setPosition((255,21), interface.NE)
      self.addWidget(l)

      #write each stat
      stats = (ST_ATTACK,
               ST_DEFENSE,
               ST_SPATTACK,
               ST_SPDEFENSE,
               ST_SPEED)     
      pointerY = 39
      pointerX = 255
      for stat in stats:
         text = str(poke.stats[stat])
         l = interface.Label(self, text)
         l.setPosition((pointerX,pointerY), interface.NE)
         self.addWidget(l)
         pointerY += 13

      #write in the exp
      pointerX = 80
      pointerY = 124
      
      l = interface.Label(self, "Exp. Points")
      self.addWidget(l, (pointerX, pointerY))
      
      l = interface.Label(self, "Next Lv.")
      self.addWidget(l, (pointerX, pointerY+14))
      
      l = interface.Label(self, str(poke.exp))
      l.setPosition((250,pointerY), interface.NE)
      self.addWidget(l)

      l = interface.Label(self, str(poke.getExpToNext()))
      l.setPosition((250, pointerY+14), interface.NE)
      self.addWidget(l)

class MovesPage(interface.Widget):
   """The moves page of the summary screen."""
   
   def __init__(self, parent, movesNode, poke, **kwargs):
      """Create the page."""

      #init widget
      fn = movesNode.getAttr("back", data.D_FILENAME)
      kwargs["background"] = fn
      interface.Widget.init(self, parent, **kwargs)

      #write the page title
      l = interface.Label(self, movesNode.getAttr("title", data.D_STRING))
      self.addWidget(l, (5,2))

      #write in each move
      #NOTE - the boxes are currently in the page image, so they show whether there's a move or not
      #at some point that wants changing I think? Needs checking
      #Also functionality to inspect moves
      pointerY = 23
      moves = poke.moves
      for move in moves:
         if move is not None:
            nameLabel = interface.Label(self, move.name)
            self.addWidget(nameLabel, (175, pointerY))

            text = "PP %i/%i" % (move.currPP, move.maxPP)
            l = interface.Label(self, text)
            l.setPosition((255, pointerY+nameLabel.height), interface.NE)
            self.addWidget(l)
            
         pointerY += 28

   def draw(self):
      self.screen.blit(self.back, self.screenLocation)

      base_menu.Widget.draw(self)





      
