import os

from . import script_yacc
from . import script_compiler
from . import script
from .commands import *

import eng.globs
import eng.data
import eng.settings

class ScriptEngine():
   """Singleton object to run scripts."""

   #use the Borg singleton model
   __shared_state = {}
   
   def __init__(self):
      """Set our internal state to be the shared state."""

      #get the shared state and use it
      self.__dict__ = self.__shared_state

   def setup(self, game, symbols):
      """
      Set up the engine to run scripts.

      Functions as an __init__ command for the singleton.

      game - the game object to act on.
      """

      #create a symbol table
      self.symbols = symbols

      #initialise variables needed to run scripts
      self.script = None
      self.result = False
      self.currentCmd = 0
      self.caller = None
      self.waitingFor = None

      self.queue = []
      
   def run(self, script, caller=None):
      """
      Run a script.

      script - the script object to run.
      caller - the object which called for the script to be run.
      """
      
      if self.script is None:
         print("-"*10)
         print("Script  with id \"{}\" called by {}".format(script.id, str(caller)))
         
         #store the current script, and caller
         self.script = script
         self.caller = caller

         #reset the command counter, and the waiting for variable
         self.currentCmd = 0
         self.waitingFor = None

         #execute the script
         self.executeScript()

      else:
         print("-"*10)
         print("Queued script with id \"{}\" called by {}".format(script.id, str(caller)))
         self.queue.append((script, caller))

   def executeScript(self):
      """
      Run the script until we have to wait for something.
      """

      #while we're not having to wait for anything, keep pulling commands from the script and executing them.
      #if we get an index error, then we've finished the script
      while self.waitingFor is None:
         try:
            cmd = self.script[self.currentCmd]
            self.handleCommand(cmd)
            self.currentCmd += 1
         except IndexError:
            self.script = None
            break

   def handleCommand(self, cmd):
      """
      Execute a single command.

      cmd - the command tuple to execute.
      """

      #split the command into the command instruction and its args
      com = cmd[0]
      args = cmd[1:]

      #with a print command, just print out the value
      if com == CMD_PRINT:
         print(args[0].evaluate(self.symbols))

      #for assignment, call the symbol table's setVar   
      elif com == CMD_ASSIGN:
         idChainNode, exprNode = args
         self.symbols.setVar(idChainNode, exprNode.evaluate(self.symbols))

      #for command assignment, execute the command then call setVar   
      elif com == CMD_COMMANDASSIGN:
         idChainNode, commandNode = args
         commandIdChainNode, argListNode = commandNode.children
         argNodeList = argListNode.children
         args = [argNode.evaluate(self.symbols) for argNode in argNodeList]
         result = self.symbols.doCommand(commandIdChainNode, args)
         self.symbols.setVar(idChainNode, result)

      #for eval, just set the result to the value   
      elif com == CMD_EVAL:
         exprNode = args[0]
         self.result = exprNode.evaluate(self.symbols)

      #for relative goto, advance the command counter however many instructions
      #there's nothing to stop this being negative if while loops ever need implementing
      elif com == CMD_GOTOREL:
         self.currentCmd += args[0]

      #for if false relative goto, only advance the counter if the result from eval is False   
      elif com == CMD_IFFALSEGOTOREL:
         if not self.result:
            self.currentCmd += args[0]

      #for a command call, evaluate each argument and then have the symbol table execute the command      
      elif com == CMD_COMMANDCALL:
         commandNode = args[0]
         idChainNode, argListNode = commandNode.children
         argNodeList = argListNode.children
         args = [argNode.evaluate(self.symbols) for argNode in argNodeList]
         self.symbols.doCommand(idChainNode, args)

      #else raise an error so we know something's wrong   
      else:
         raise KeyError

   def tick(self):
      """Tick the script engine."""

      #tick symbol table
      self.symbols.tick()

      #print(self.script, self.queue)

      #if we have a script, then check whether we're waiting for something
      #if not, run the script
      #if we are waiting, then check whether the object we're waiting for has finished
      #if so, stop waiting and run the script      
      if self.script is not None:
         if self.waitingFor is None:
            self.executeScript()
         else:
            if not self.waitingFor.busy:
               self.waitingFor = None
               self.executeScript()
               
      if (self.script is None) and self.queue:
         script, caller = self.queue.pop()
         self.run(script, caller)
