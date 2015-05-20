import xml.etree.ElementTree as ET

from modules.property_view import PropertyView

class IdProperty(PropertyView):
   def __init__(self, master):
      PropertyView.__init__(self, master, "ID")

   def loadData(self, node):
      self.val = node.attrib.get("id", "")

   def isValid(self):
      return True

   def dumpOnto(self, node):
      node.attrib["id"] = self.val

class TilesetProperty(PropertyView):
   def __init__(self, master):
      PropertyView.__init__(self, master, "Tileset")

   def loadData(self, node):
      self.val = node.attrib.get("tileset", "")

   def isValid(self):
      return True

   def dumpOnto(self, node):
      node.attrib["tileset"] = self.val

class PositionProperty(PropertyView):
   def __init__(self, master):
      PropertyView.__init__(self, master, "Position")

   def loadData(self, node):
      self.val = node.attrib.get("position", "")

   def isValid(self):
      return True

   def dumpOnto(self, node):
      node.attrib["position"] = self.val

class LevelProperty(PropertyView):
   def __init__(self, master):
      PropertyView.__init__(self, master, "Level")

   def loadData(self, node):
      self.val = node.attrib.get("level", "")

   def isValid(self):
      return True

   def dumpOnto(self, node):
      node.attrib["level"] = self.val

class MovementProperty(PropertyView):
   def __init__(self, master):
      PropertyView.__init__(self, master, "Movement")

   def loadData(self, node):
      movementNode = node.find("movement")
      if movementNode is not None:
         self.val = movementNode.attrib.get("type", "")
      else:
         self.val = ""

   def isValid(self):
      return True

   def dumpOnto(self, node):
      if self.val:
         movementNode = node.find("movement")
         if movementNode is None:
            movementNode = ET.Element("movement")
            node.append(movementNode)
         movementNode.attrib["type"] = self.val

class RadiusProperty(PropertyView):
   def __init__(self, master):
      PropertyView.__init__(self, master, "Radius")

   def loadData(self, node):
      movementNode = node.find("movement")
      if movementNode is not None:
         self.val = movementNode.attrib.get("radius", "")
      else:
         self.val = ""

   def isValid(self):
      return True

   def dumpOnto(self, node):
      if self.val:
         movementNode = node.find("movement")
         if movementNode is None:
            movementNode = ET.Element("movement")
            node.append(movementNode)
         movementNode.attrib["radius"] = self.val

class CourseProperty(PropertyView):
   def __init__(self, master):
      PropertyView.__init__(self, master, "Course")

   def loadData(self, node):
      movementNode = node.find("movement")
      if movementNode is not None:
         self.val = movementNode.attrib.get("course", "")
      else:
         self.val = ""

   def isValid(self):
      return True

   def dumpOnto(self, node):
      if self.val:
         movementNode = node.find("movement")
         if movementNode is None:
            movementNode = ET.Element("movement")
            node.append(movementNode)
         movementNode.attrib["course"] = self.val

class ScriptIdProperty(PropertyView):
   def __init__(self, master):
      PropertyView.__init__(self, master, "Script ID")

   def loadData(self, node):
      scriptNode = node.find("script")
      if scriptNode is not None:
         self.val = scriptNode.attrib.get("id", "")
      else:
         self.val = ""

   def isValid(self):
      return True

   def dumpOnto(self, node):
      if self.val:
         scriptNode = node.find("script")
         if scriptNode is None:
            scriptNode = ET.Element("script")
            node.append(scriptNode)
         scriptNode.attrib["id"] = self.val

class ScriptTriggerProperty(PropertyView):
   def __init__(self, master):
      PropertyView.__init__(self, master, "Script trigger")

   def loadData(self, node):
      scriptNode = node.find("script")
      if scriptNode is not None:
         self.val = scriptNode.attrib.get("trigger", "")
      else:
         self.val = ""

   def isValid(self):
      return True

   def dumpOnto(self, node):
      if self.val:
         scriptNode = node.find("script")
         if scriptNode is None:
            scriptNode = ET.Element("script")
            node.append(scriptNode)
         scriptNode.attrib["trigger"] = self.val
   
class TargetMapProperty(PropertyView):
   def __init__(self, master):
      PropertyView.__init__(self, master, "Target map")

   def loadData(self, node):
      self.val = node.attrib.get("targetmap", "")

   def isValid(self):
      return True

   def dumpOnto(self, node):
      node.attrib["targetmap"] = self.val

class TargetPositionProperty(PropertyView):
   def __init__(self, master):
      PropertyView.__init__(self, master, "Target position")

   def loadData(self, node):
      self.val = node.attrib.get("targetposition", "")

   def isValid(self):
      return True

   def dumpOnto(self, node):
      node.attrib["targetposition"] = self.val

class TriggerProperty(PropertyView):
   def __init__(self, master):
      PropertyView.__init__(self, master, "Trigger")

   def loadData(self, node):
      self.val = node.attrib.get("trigger", "")

   def isValid(self):
      return True

   def dumpOnto(self, node):
      node.attrib["trigger"] = self.val

class TypeProperty(PropertyView):
   def __init__(self, master):
      PropertyView.__init__(self, master, "Type")

   def loadData(self, node):
      self.val = node.attrib.get("type", "")

   def isValid(self):
      return True

   def dumpOnto(self, node):
      node.attrib["type"] = self.val
