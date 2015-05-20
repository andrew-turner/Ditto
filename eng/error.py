class DevError(Exception):
   """Exception caused by a problem with the resources supplied to Ditto."""

   def __init__(self, *args):
      self.lines = args
   
   def describe(self):
      """Return a list of strings to print out."""
      
      return self.lines

