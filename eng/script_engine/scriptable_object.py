from . import script_error

class ScriptableObject(object):
   """Inherited by objects to allow scripting access to them."""
   
   def __init__(self):
      """Set up the object's commands directory."""

      #initialise the dict, commands to be added by objects
      #TODO maybe put some kind of dir() command, although possibly better done by documentation?
      self.scriptCommands = {}

   def getObject(self, name):
      """
      Return an object based on a specified name.

      name - the objects name as given in the script.
      """

      #raise an error
      #should be overridden to allow something like PLAYER.party.pokemon to work
      raise script_error.DLookupError(name)

   def getVarFromNode(self, idChainNode):
      """
      Either get the variable if it's in our space, or delegate to the next in line.

      Should not be overridden.

      idChainNode - the top node in an identifier chain.
      """

      #if the node has a child, then delegate the rest of the chain to that object
      if idChainNode.children:
         nextNode = idChainNode.children[0]
         obj = self.getObject(idChainNode.leaf)
         return obj.getVarFromNode(nextNode)

      #else if we're the last node in the chain, get the requested variable
      else:
         try:
            return self.getVar(idChainNode.leaf)
         except script_error.DLookupError:
            return self.getObject(idChainNode.leaf)

   def getVar(self, name):
      """
      Get a variable with a given name.

      name - the variable's name.
      """

      #raise an error
      #should be overridden in most classes
      raise script_error.DLookupError(name)

   def setVarFromNode(self, idChainNode, val):
      """
      Either set the variable if it's in our space, else delegate to the next in line.

      Should not be overridden.

      idChainNode - the top node in an identifier chain.
      val - the value to set the variable to.
      """

      #if the node has a child, then delegate the rest of the chain to that object
      if idChainNode.children:
         nextNode = idChainNode.children[0]
         obj = self.getObject(idChainNode.leaf)
         obj.setVarFromNode(nextNode, val)

      #else if we're the last node in the chain, set the requested variable
      else:
         self.setVar(idChainNode.leaf, val)

   def setVar(self, name, val):
      """
      Set a variable with a given name to a given value.
      """

      #raise an error
      #should be overridden in most classes
      raise script_error.DLookupError(name)

   def doCommand(self, idChainNode, args=[]):
      """
      Either execute a command if it's in our space, else delegate to the next in line.

      Returns the return value of the command.
      """

      #if the node has a child, then delegate the rest of the chain to that object
      if idChainNode.children:
         nextNode = idChainNode.children[0]
         obj = self.getObject(idChainNode.leaf)
         return obj.doCommand(nextNode, args)

      #else if we're the last node on the chain, execute the requested command, returning the return value
      else:
         try:
            command = getattr(self, "command_{}".format(idChainNode.leaf))
         except AttributeError:
            raise script_error.DLookupError(idChainNode.leaf)
         return command(*args)
