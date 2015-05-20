import eng.pokemon as pokemon
import eng.items as items
import eng.foreground_object as foreground_object
import eng.sound as sound
import eng.script_engine as script_engine
import eng.error as error

from eng.constants.directions import *

def raiseNameError(name, scriptId, fn, lineNo):
   raise error.DevError("Unable to find object: {}".format(name),
                        "In script named \"{}\".".format(scriptId),
                        "Defined in file:",
                        fn,
                        "At line number {}.".format(lineNo))

class Symbols():
   def __init__(self, game):
      self.game = game
      self.scriptEngine = script_engine.ScriptEngine()

      self.counter = None
      
      self.locals = {}
      self.commands = {"foo": self.command_foo,
                       "lock": self.command_lock,
                       "unlock": self.command_unlock,
                       "facePlayer": self.command_facePlayer,
                       "dialog": self.command_dialog,
                       "choiceDialog": self.command_choiceDialog,
                       "generatePokemon": self.command_generatePokemon,
                       "generateItem": self.command_generateItem,
                       "waitFor": self.command_waitFor,
                       "waitFrames": self.command_waitFrames,
                       "fadeOutAndIn": self.command_fadeOutAndIn,
                       "playSoundEffect": self.command_playSoundEffect}

   def getObject(self, objName):
      if objName == "PLAYER":
         return self.game.player
      elif objName == "CALLER":
         return self.scriptEngine.caller
      elif objName == "MAP":
         return self.game.player.map
      elif objName == "SAVE":
         return self.game.savegame
      elif objName == "CAMERA":
         return self.game.camera
      elif objName == "PARTY":
         return self.game.party
      elif objName == "BAG":
         return self.game.bag
      else:
         raise script_engine.DLookupError(objName)

   def getVar(self, idChainNode):
      if idChainNode.children:
         nextNode = idChainNode.children[0]
         try:
            obj = self.getObject(idChainNode.leaf)
         except script_engine.DLookupError as e:
            raiseNameError(e.name, idChainNode.scriptId, idChainNode.fn, idChainNode.lineno)
         try:
            return obj.getVarFromNode(nextNode)
         except script_engine.DLookupError as e:
            raiseNameError(e.name, idChainNode.scriptId, idChainNode.fn, idChainNode.lineno)
      else:
         try:
            return self.locals[idChainNode.leaf]
         except KeyError:
            try:
               return self.getObject(idChainNode.leaf)
            except KeyError:
               raiseNameError(e.name, idChainNode.scriptId, idChainNode.fn, idChainNode.lineno)

   def setVar(self, idChainNode, val):
      if idChainNode.children:
         nextNode = idChainNode.children[0]
         obj = self.getObject(idChainNode.leaf)
         try:
            obj.setVarFromNode(nextNode, val)
         except script_engine.DLookupError as e:
            raiseNameError(e.name, idChainNode.scriptId, idChainNode.fn, idChainNode.lineno)
      else:
         self.locals[idChainNode.leaf] = val

   def doCommand(self, idChainNode, args=[]):
      if idChainNode.children:
         nextNode = idChainNode.children[0]
         try:
            obj = self.getObject(idChainNode.leaf)
         except script_engine.DLookupError as e:
            raiseNameError(e.name, idChainNode.scriptId, idChainNode.fn, idChainNode.lineno)
         try:
            return obj.doCommand(nextNode, args)
         except script_engine.DLookupError as e:
            raiseNameError(e.name, idChainNode.scriptId, idChainNode.fn, idChainNode.lineno)            
      else:
         try:
            command = self.commands[idChainNode.leaf]
         except KeyError:
            raiseNameError(e.name, idChainNode.scriptId, idChainNode.fn, idChainNode.lineno)
         return command(*args)

   def tick(self):
      if self.counter is not None:
         self.counter.tick()
         if not self.counter.busy:
            self.counter = None

   def command_foo(self, *args):
      if args:
         print("Called foo with args: %s" % str(args))
      else:
         print("Called foo with no arg")

   def command_lock(self):
      self.game.player.lock()
      try:
         self.scriptEngine.caller.lock()
      except AttributeError:
         pass

   def command_unlock(self):
      self.game.player.unlock()
      try:
         self.scriptEngine.caller.unlock()
      except AttributeError:
         pass

   def command_facePlayer(self):
      difference = (self.game.player.position[0]-self.scriptEngine.caller.position[0],
                    self.game.player.position[1]-self.scriptEngine.caller.position[1])
      if difference == (0, -1): #if player is above caller
         self.scriptEngine.caller.direction = DIR_UP
      elif difference == (0, 1): #if player is below caller
         self.scriptEngine.caller.direction = DIR_DOWN
      elif difference == (-1, 0): #if player is to left of caller
         self.scriptEngine.caller.direction = DIR_LEFT
      elif difference == (1, 0): #if player is to right of caller
         self.scriptEngine.caller.direction = DIR_RIGHT

   def command_dialog(self, text, last=False, colour="main"):
      d = self.game.makeDialog(text, not last, colour)
      self.game.foregroundObject = d
      self.scriptEngine.waitingFor = d

   def command_choiceDialog(self, text, *choices):
      d = self.game.makeChoiceDialog(text, choices)
      self.game.foregroundObject = d
      self.scriptEngine.waitingFor = d

   def command_generatePokemon(self, species, level):
      return pokemon.Pokemon(species, level)

   def command_generateItem(self, name):
      return items.Item(name)

   def command_waitFor(self, obj):
      self.scriptEngine.waitingFor = obj

   def command_waitFrames(self, n):
      c = Counter(n)
      self.counter = c
      self.scriptEngine.waitingFor = c

   def command_fadeOutAndIn(self, n):
      self.game.foregroundObject = foreground_object.FadeOutAndIn(self.game.screen, n)

   def command_playSoundEffect(self, name):
      try:
         e = sound.SOUNDEFFECTS[name]
         sound.playEffect(e)
         
      except KeyError:
         sound.playEffect(name)

class Counter():
   def __init__(self, n):
      self.count = n

      self.busy = True

   def tick(self):
      self.count -= 1

      if self.count <= 0:
         self.busy = False

