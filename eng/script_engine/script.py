import os

from . import script_yacc
from . import script_compiler

import eng.settings as settings
import eng.data as data
import eng.error as error

from eng.constants.events import *

#files to print out debug info to
OUT_AST = ".\\ast.txt"
OUT_CMDS = ".\\cmds.txt"

#separator used in script files between scripts
SCRIPTSEP = "###"

def scriptFromText(source, fn, scriptId, trigger=None):
   return Script(source, fn, scriptId, trigger)

def scriptFromNode(node, defaultFile=None):
   #determine trigger
   triggerName = node.getOptionalAttr("trigger", data.D_STRING)
   trigger = TRIGGERNAMES.get(triggerName, None)

   #get the path to the script file and the script id
   scriptId = node.getAttr("id", data.D_STRING)

   if defaultFile:
      fn = node.getOptionalAttr("source", data.D_FILENAME)
      if fn is None:
         fn = defaultFile
   else:
      fn = node.getAttr("source", data.D_FILENAME)

   #get the source code of the scrip, and have yacc build an AST
   source = getSource(fn, scriptId)

   #return a Script object
   return Script(source, fn, scriptId, trigger)

def getSource(fn, scriptId):
   """
   Gets the source code for a specified script from a scripts declaration file.

   fn - the filename of the scripts file.
   scriptId - the id of the script.
   """

   #open the file, read it and close
   f = open(fn, "r")
   lines = f.readlines()
   f.close()

   #work out what the title will be for the given scriptId
   title = "%s%s%s" % (SCRIPTSEP, scriptId, SCRIPTSEP)

   #find the lines of code
   #iterate over each line, when we find the title, start adding code lines to the list
   #do this until we find the start of the next script, at which point we can stop
   code = []
   inCode = False
   for i in range(0, len(lines)):
      line = lines[i]
      if not inCode:
         if line.startswith(title):
            inCode = True
      else:
         if line.startswith(SCRIPTSEP):
            inCode = False
            break
         else:
            code.append(line)

   #if we didn't find the script in the file, raise an error
   if not code:
      raise error.DevError("Unable to find the script named \"{}\".".format(scriptId),
                           "Should be defined in file:",
                           fn)

   #return the lines all joined together into one string for lex input
   return "".join(code)        
   

class Script():
   """Script object which opens and compiles scripts."""
   
   def __init__(self, source, fn, scriptId, trigger=None):
      """Find the script source and compile it to commands."""

      self.id = scriptId

      #determine the script's trigger if it has one
      self.trigger = trigger  

      #parse to AST
      ast = script_yacc.parse(source, fn, scriptId)

      #write out the AST for debugging
      #writeAST(ast, OUT_AST)

      #compile the AST to commands
      self.commands = script_compiler.toCommands(ast)

      #write out commands for debugging
      #writeCommands(self.commands, OUT_CMDS)

   def __getitem__(self, i):
      """Return the command at the requested index."""
      return self.commands[i]

   def __repr__(self):
      return "<script \"{}\">".format(self.id)

#for debugging
def writeAST(ast, fn):
   f = open(fn, "w")
   ast.pprint(f)
   f.close()

def writeCommands(commands, fn):
   f = open(fn, "w")
   for cmd in commands:
      f.write(str(cmd))
      f.write("\n")
   f.close()
      
      
      
