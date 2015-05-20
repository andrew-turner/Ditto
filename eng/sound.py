import threading
import os
import xml.etree.ElementTree as ET

import pygame

from . import settings
from . import globs
from . import data

#initialise constants
SD_SAVE = 0
SD_BUMP = 1
SD_SELECT = 2
SD_CHOOSE = 3
SD_JUMP = 4
SD_PUSH = 5
SD_MENUOPEN = 6

#define the names used to refer to sound effects in the XML file
SOUNDEFFECTS = {"SAVE": SD_SAVE,
                "BUMP": SD_BUMP,
                "SELECT": SD_SELECT,
                "CHOOSE": SD_CHOOSE,
                "JUMP": SD_JUMP,
                "PUSH": SD_PUSH,
                "MENUOPEN": SD_MENUOPEN}

#initialise dictionary for mapping effects to sound files
effects = {}

#initialise dictionary to hold playing effects
currentEffects = {}

#remember the current playing music
currentMusic = None

def init(fn):
   """
   Initialise the pygame mixer and parse XML file for sound effect locations.

   fn - the path to the XML file.
   """

   #initialise the pygame mixer
   pygame.mixer.init()

   #parse the XML file
   root = data.getTreeRoot(fn)
   for effect in root.getChildren("soundeffect"):
      name = effect.getAttr("name", data.D_STRING)
      try:
         e = SOUNDEFFECTS[name]
         effects[e] = os.path.join(settings.path, "data", effect.getAttr("file", data.D_STRING))
         
      except KeyError:
         effects[name] = os.path.join(settings.path, "data", effect.getAttr("file", data.D_STRING))

def playMusic(fn):
   """
   Play a music track.

   fn - the path to the track.
   """

   global currentMusic

   #if music is enabled, start a thread to play the music
   #music loading is slow, but not needed instantly so threading is a good idea
   #especially as it usually happens at processing bottleneck frames like map transfers
   if (currentMusic != fn) and settings.music:
      currentMusic = fn
      t = threading.Thread(target=threadPlayMusic, args=(fn,))
      t.start()

def threadPlayMusic(fn):
   """
   Function to be called by playMusic, to run in a separate thread.

   fn - path to the music file to load.
   """

   #load the music and play it on loop
   pygame.mixer.music.load(fn)
   pygame.mixer.music.play(-1)

def playEffect(effect):
   """
   Play a sound effect.

   Checks to see whether the effect is currently playing, and won't play again if so.

   effect - the effect to play.
   """

   #if sound effects are enabled, then start doing stuff
   if settings.soundEffects:

      #make a list of keys for effects that have finished playing and delete them
      keys = [k for k in currentEffects if not currentEffects[k].get_busy()]
      for key in keys:
         del(currentEffects[key])

      #if the requested effect is not already playing, play it   
      if effect not in currentEffects:
         channel = pygame.mixer.Sound(effects[effect]).play()
         currentEffects[effect] = channel


