import pygame
from pygame.locals import *

import eng.settings as settings

from eng.constants.buttons import *

#initialise lists to hold key information  
keysDown = []
keysJustPressed = []
keysJustReleased = []

#!!!!!!!!!!!!!!
#TODO
#key mappings need to reflect settings
#settings needs a proper reworking anyway...

def processEvents():
   """
   Poll all pygame events and update key data.

   Returns True if there's a Quit event, otherwise False.
   """

   #clear lists
   del keysJustPressed[:]
   del keysJustReleased[:]
   del keysDown[:]

   #iterate through all events since the last call   
   for e in pygame.event.get():

      #if there's a Quit event, return True
      if e.type == QUIT:
         return True

      #if it's a keydown, and we care about it,
      #add to the list of keys down, and keys just pressed this frame
      elif e.type == KEYDOWN:
         if e.key in settings.keys:
            mappedKey = settings.keys[e.key]
            keysJustPressed.append(mappedKey)

      #if it's a keyup, and we care about it,
      #remove from the list of keys down, and add to keys just released this frame
      elif e.type == KEYUP:
         if e.key in settings.keys:
            mappedKey = settings.keys[e.key]
            keysJustReleased.append(mappedKey)

      #no Quit events, so return False            
      return False

   #check for keys down
   #needs work to reflect settings
   keys = pygame.key.get_pressed()
   if keys[pygame.locals.K_UP]:
      keysDown.append(BT_UP)
   if keys[pygame.locals.K_DOWN]:
      keysDown.append(BT_DOWN)
   if keys[pygame.locals.K_LEFT]:
      keysDown.append(BT_LEFT)
   if keys[pygame.locals.K_RIGHT]:
      keysDown.append(BT_RIGHT)
   if keys[pygame.locals.K_SPACE]:
      keysDown.append(BT_TURBO)

def get():
   """Return a 3-tuple of keys down, keys pressed since last call, and keys released since last call."""
   
   return (keysDown, keysJustPressed, keysJustReleased)
