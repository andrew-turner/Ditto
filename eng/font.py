import os

import pygame

from . import settings
from . import data
from . import globs
from . import error

###NOTE
#right now, the font loads all the letters on initialization
#we could make it lazy, which might spread the cpu load across frames, but would have a memory overhead...

#the character sequence used to indicate a new line should be started
LINESEP = "$$"

class Font(object):
   """Class to load fonts and write with them."""
   
   def __init__(self, fn):
      """
      Load the image and cut out the individual characters.

      fn - the font XML file.
      """

      #parse the XML file
      root = data.getTreeRoot(fn)
      path = os.path.join(settings.path, "data", root.getAttr("file", data.D_STRING))
      self.height = root.getAttr("height", data.D_INT)
      transparency = root.getAttr("transparency", data.D_INT3LIST)

      #load the image
      image = data.getImage(path, fn)
      image.set_colorkey(transparency)

      #set up dictionarys for different character sets
      self.colours = {} #{colourName: {character: image}}
      self.colourShorts = {} #{shortName: colourName}
      colourOffsets = {} #{colourName: offset}

      #add the main colour in place automatically
      #if it's later defined in the file, it'll get overridden
      self.colours["main"] = {}
      colourOffsets["main"] = (0,0)

      #for each defined colour, create a dict for the characters
      #if there's a short name defined, add in to the right dict
      for colourNode in root.getChildren("colour"):
         d = {}
         colName = colourNode.getAttr("name", data.D_STRING)
         self.colours[colName] = d
         colourOffsets[colName] = colourNode.getAttr("offset", data.D_INT2LIST)
         
         colShort = colourNode.getOptionalAttr("short", data.D_STRING)
         if colShort is not None:
            self.colourShorts[colShort] = colName

      #cut out the tiles and store them in the dictionaries
      for c in root.getChildren("character"):
         char = c.getAttr("char", data.D_STRING)
         width = c.getAttr("width", data.D_INT)
         location = c.getAttr("location", data.D_INT2LIST)

         for col in self.colours:
            offset = colourOffsets[col]
            self.colours[col][char] = image.subsurface(location[0]+offset[0], location[1]+offset[1], width, self.height)

   def _parseText(self, text, defaultColour="main"):
      """
      Parse the text for colour tags.

      Returns a list of (colour, text) tuples to render.

      text - the text to parse.
      defaultColour - the starting colour to use.
      """

      ###NOTE
      #currently it doesn't mind if the tags aren't balanced,
      #so "This [r]text." would be valid
      #maybe it should force the tags to be closed?

      #initialise the colour stack with the starting colour
      colourStack = [defaultColour]

      #init result list
      result = []

      #this will track where we are up to in the text
      i = 0

      #while we're still in the text, we can look for tags
      while i < len(text):

         #get the position of the next left bracket
         #if we don't find one, then there's no more tags and we're done
         pos = text[i:].find("[")
         if pos == -1:
            break

         #look from there for a right bracket
         #if we don't find one, then we have an unclosed tag so raise an error
         step = text[i+pos:].find("]")
         if step == -1:
            print("Found opening bracket but no closing.")
            raise TypeError

         #get the actual text from the tag
         #step is relative to i+pos
         tag = text[i+pos+1: i+pos+step]

         #since we found a tag, add everything up to this position with the old colour
         result.append((colourStack[-1], text[i: i+pos]))

         #if it's a closing tag, then get the name from it
         #if we can't find it as a colour name, check short names, else raise an error
         #make sure that the closing tag matches the current colour, and then remove the current colour
         #if it doesn't, raise an error
         if tag[0] == "/":
            name = tag[1:]
            if not name in self.colours:
               try:
                  name = self.colourShorts[name]
               except KeyError:
                  print("Couldn't identify colour: %s" % name)
                  raise KeyError
            if colourStack[-1] == name:
               colourStack.pop()
            else:
               print("Closing tag %s doesn't match current colour %s." % (tag, colourStack[-1]))
               raise TypeError

         #otherwise it's opening tag
         #if we have that colour, add it to the stack
         #else, check in short names, and add the proper name to the stack
         #else raise an error
         else:
            if tag in self.colours:
               colourStack.append(tag)
            else:
               try:
                  name = self.colourShorts[tag]
               except KeyError:
                  raise KeyError
               colourStack.append(name)

         #update the current position pointer
         i += pos+step+1

      #when we're done, add the last bit of text to the result and return
      result.append((colourStack[-1], text[i:]))

      return result

   def writeText(self, text, surface, location, **kwargs):
      """
      Write text to a given surface at a given location.

      text - the string to write
      surface - the surface to write onto
      location - the coordinates on the surface to start drawing at

      keywords:
        colour - the defult colour to use. Defaults to "main".
        numChars - the number of characters to render (for dialogs). Defaults to all.
        spacer - the space between lines of text. Defaults to 1 pixel.
      """

      #load keyword args
      defaultColour = kwargs.get("colour", "main")
      numChars = kwargs.get("chars", -1)
      spacer = kwargs.get("spacer", 1)

      #init count of characters
      charCount = 0

      #split the lines up, and for each line, render the text
      pointerY = location[1]
      for line in text.split("$$"):
         pointerX = location[0]

         #parse the line for colours
         #for each partial string returned, render it in the correct colour
         #raise an error if any of the characters isn't supported
         parsed = self._parseText(line, defaultColour)
         for colour, chars in parsed:
            colChars = self.colours[colour]
            for char in chars:
               try:
                  im = colChars[char]
               except KeyError:
                  raise error.DInvalidResourceError("Font file", "Character %s" % char)

               surface.blit(im, (pointerX, pointerY))
               pointerX += im.get_width()

               #keep a count of how many characters have been rendered
               #if we've done enough then finish
               charCount += 1
               if (numChars >= 0) and (charCount >= numChars):
                  return
               
         pointerY += self.height + spacer

   def calcWidth(self, text):
      """Calculate how wide text would be if written in this font."""

      #return the sum of the widths of the characters
      return max( sum([self.colours["main"][char].get_width() for char in line]) for line in text.split(LINESEP))   
