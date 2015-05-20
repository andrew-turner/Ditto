import os
import xml.etree.ElementTree as ET

import pygame

from . import error
from . import globs
import eng.settings as settings

D_STRING = 0
D_INT = 1
D_INTLIST = 2
D_INT2LIST = 3
D_INT3LIST = 4
D_FILENAME = 5

def getTreeRoot(path, fn="Unknown file"):
   """
   Use a filename to create an XML tree and return the root node.

   path - the path to the XML file.
   fn - the file from which the XML file was requested.
   """

   #try to open it
   #if there's an error, raise the relevant exception.
   try:
      tree = ET.parse(path)
   except ET.ParseError:
      raise error.DevError("Not a valid XML file:",
                            path,
                            "As requested from file:",
                            fn)
   except IOError:
      raise error.DevError("File not accessible (probably doesn't exist):",
                            path,
                            "As requested from file:",
                            fn)

   root = tree.getroot()

   res = DittoNode(root, path)
   
   return res

def getImage(imagePath, fn="Unknown file"):
   """
   Open an image filename to a pygame surface.

   imagePath - the path to the image file
   fn - the file from which the image was requested
   """

   #try to open the file
   #if it doesn't work, raise the relevant exception
   try:
      return pygame.image.load(imagePath)
   except:
      raise error.DevError("Not a good image file:",
                           imagePath,
                           "As requested from file:",
                           fn)

def check(exp, resourcePath, fn="Unknown file"):
   """
   Perform a boolean check to make sure a resource is suitable.

   If exp evaluates to False, raises an exception.

   exp - the expression to evaluate.
   resourcePath - the path to the resource that the check is relevant to.
   fn - the file from which the resource was requested.
   """
   
   if not exp:
      raise error.DInvalidResourceError(fn, resourcePath)

def formatAttr(att, formatting):
   """
   Format an attribute string into the correct form.

   att - the attribute.
   formatting - the formatting constant.   
   """

   #depending on the requested formatting format, get the attribute into the required style
   #if it doesn't match the style requested, raise an exception
   
   if formatting == D_STRING:
      return att
      
   elif formatting == D_INT:
      try:
         return int(att)
      except ValueError:
         raise error.DevError("Invalid the attribute {} from node {}.".format(attribute, self._elem.tag),
                               "Attribute must be an integer.",
                               "In file:",
                               self.ditto_fn)

   elif formatting == D_INTLIST:
      try:
         return list(map(int, att.split(",")))
      except ValueError:
         raise error.DevError("Invalid the attribute {} from node {}.".format(attribute, self._elem.tag),
                               "Attribute must be a list of integers.",
                               "In file:",
                               self.ditto_fn)
         
   elif formatting == D_INT2LIST:
      try:
         return list(map(int, att.split(",")))
      except ValueError:
         raise error.DevError("Invalid the attribute {} from node {}.".format(attribute, self._elem.tag),
                               "Attribute must be a list of 2 integers.",
                               "In file:",
                               self.ditto_fn)
      if len(ans) != 2:
         raise error.DevError("Invalid the attribute {} from node {}.".format(attribute, self._elem.tag),
                               "Attribute must be a list of 2 integers.",
                               "In file:",
                               self.ditto_fn)

   elif formatting == D_INT3LIST:
      try:
         return list(map(int, att.split(",")))
      except ValueError:
         raise error.DevError("Invalid the attribute {} from node {}.".format(attribute, self._elem.tag),
                               "Attribute must be a list of 3 integers.",
                               "In file:",
                               self.ditto_fn)
      if len(ans) != 3:
         raise error.DevError("Invalid the attribute {} from node {}.".format(attribute, self._elem.tag),
                               "Attribute must be a list of 3 integers.",
                               "In file:",
                               self.ditto_fn)

   elif formatting == D_FILENAME:
      return os.path.join(settings.path, "data", att)

   raise ValueError(formatting)

class DittoNode():
   """
   An single node in the XML tree.

   getAttr(attribute, formatting)
   getOptionalAttr(attribute, formatting, default=None)
   getChild(name)
   getOptionalChild(name)
   getChildren(name=None)

   ditto_fn
   """
   
   def __init__(self, elem, fn=None):
      """
      Init the node from the ElementTree element.

      elem - the ElementTree element.
      fn - the filename it belongs to.
      """

      #store the element and fn
      self._elem = elem

      self.tag = elem.tag
      self.ditto_fn = fn

   def getAttr(self, attribute, formatting):
      """
      Get an attribute from the node, putting it to the required format.

      attribute - the attribute to get.
      formatting - the style to return the data in.
      """

      #try to get the raw attribute
      #if it doesn't exist, raise the relevant exception
      try:
         att = self._elem.attrib[attribute]
      except KeyError:
         raise error.DevError("Missing the attribute {} from node {}.".format(attribute, self._elem.tag),
                               "In file:",
                               self.ditto_fn)

      return formatAttr(att, formatting)      

   def getOptionalAttr(self, attribute, formatting, default=None):
      """
      Get an attribute from a node if it exists, putting it to the required format.

      attribute - the attribute to get.
      formatting - the style to return the data in.
      default - the value to return if the attribute is not found.
      """

      #try to get the raw attribute
      #if it doesn't exist, raise the relevant exception
      try:
         att = self._elem.attrib[attribute]
      except KeyError:
         return default

      return formatAttr(att, formatting)

   def getChild(self, name):
      #try to find the child node
      #if it isn't found, raise the relevant exception
      e = self._elem.find(name)
      if e is None:
         raise error.DevError("Missing the child node {} from node {}.".format(name, self._elem.tag),
                               "In file:",
                               self.ditto_fn)

      return DittoNode(e, self.ditto_fn)

   def getOptionalChild(self, name):
      #try to find the child node
      #if it isn't found, raise the relevant exception
      e = self._elem.find(name)
      if e is None:
         return None

      return DittoNode(e, self.ditto_fn)

   def getChildren(self, name=None):
      """
      Get all the child nodes of a certain name from a parent node.

      Returns an empty list if none are found.

      node - the parent node.
      name - the name of the child nodes.
      """

      #get any child nodes
      if name is not None:
         elems = self._elem.findall(name)
      else:
         elems = [child for child in self._elem]

      return [DittoNode(e, self.ditto_fn) for e in elems]


