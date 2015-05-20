import error

class InterfaceError(error.DittoError):
   pass

class DMissingKeywordError(InterfaceError):
   def __init__(self, widget, keyword):
      self.w = widget
      self.keyword = keyword

   def describe(self):
      
