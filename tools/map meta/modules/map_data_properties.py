import xml.etree.ElementTree as ET

from modules.property_view import PropertyView

class IdProperty(PropertyView):
   def __init__(self, master):
      PropertyView.__init__(self, master, "ID")

   def loadData(self, root):
      self.val = root.attrib.get("id", "")

   def isValid(self):
      return True

   def dumpOnto(self, root):
      root.attrib["id"] = self.val

class MapFileProperty(PropertyView):
   def __init__(self, master):
      PropertyView.__init__(self, master, "Map file")

   def loadData(self, root):
      self.val = root.attrib.get("file", "")

   def isValid(self):
      return True

   def dumpOnto(self, root):
      root.attrib["file"] = self.val

class TilesetProperty(PropertyView):
   def __init__(self, master):
      PropertyView.__init__(self, master, "Tileset")

   def loadData(self, root):
      self.val = root.attrib.get("tileset", "")

   def isValid(self):
      return True

   def dumpOnto(self, root):
      root.attrib["tileset"] = self.val

class MusicProperty(PropertyView):
   def __init__(self, master):
      PropertyView.__init__(self, master, "Music")

   def loadData(self, root):
      self.val = root.attrib.get("music", "")

   def isValid(self):
      return True

   def dumpOnto(self, root):
      root.attrib["music"] = self.val

class NameProperty(PropertyView):
   def __init__(self, master):
      PropertyView.__init__(self, master, "Name")

   def loadData(self, root):
      self.val = root.attrib.get("name", "")

   def isValid(self):
      return True

   def dumpOnto(self, root):
      if self.val:
         root.attrib["name"] = self.val

class ScriptFileProperty(PropertyView):
   def __init__(self, master):
      PropertyView.__init__(self, master, "Script file")

   def loadData(self, root):
      self.val = root.find("scriptfile").attrib.get("source", "")

   def isValid(self):
      return True

   def dumpOnto(self, root):
      if self.val:
         node = ET.Element("scriptfile")
         node.attrib["source"] = self.val
         root.append(node)

class WeatherProperty(PropertyView):
   def __init__(self, master):
      PropertyView.__init__(self, master, "Weather")

   def loadData(self, root):
      weatherNode = root.find("weather")
      if weatherNode is not None:
         self.val = weatherNode.attrib.get("type", "")

   def isValid(self):
      return True

   def dumpOnto(self, root):
      if self.val:
         node = ET.Element("weather")
         node.attrib["type"] = self.val
         root.append(node)

class LoadScriptProperty(PropertyView):
   def __init__(self, master):
      PropertyView.__init__(self, master, "Load script")

   def loadData(self, root):
      scriptNodes = root.findall("script")

      loadScriptNode = None
      for scriptNode in scriptNodes:
         if scriptNode.attrib.get("trigger", "") == "load":
            loadScriptNode = scriptNode
            break
      
      if loadScriptNode is not None:
         self.val = loadScriptNode.attrib.get("id", "")

   def isValid(self):
      return True

   def dumpOnto(self, root):
      if self.val:
         node = ET.Element("script")
         node.attrib["id"] = self.val
         node.attrib["trigger"] = "load"
         root.append(node)

class LeftConnectionProperty(PropertyView):
   def __init__(self, master):
      PropertyView.__init__(self, master, "Left connection")

   def loadData(self, root):
      for connNode in root.findall("connection"):
         if connNode.attrib["side"] == "left":
            node = connNode
            break
      else:
         self.val = ""
         return

      self.val = node.attrib.get("map", "")

   def isValid(self):
      return True

   def dumpOnto(self, root):
      if self.val:
         for connNode in root.findall("connection"):
            if connNode.attrib["side"] == "left":
               node = connNode
               break
         else:
            node = ET.Element("connection")
            node.attrib["side"] = "left"
            root.append(node)
         
         node.attrib["map"] = self.val
         

class LeftOffsetProperty(PropertyView):
   def __init__(self, master):
      PropertyView.__init__(self, master, "Left offset")

   def loadData(self, root):
      for connNode in root.findall("connection"):
         if connNode.attrib["side"] == "left":
            node = connNode
            break
      else:
         self.val = ""
         return

      self.val = node.attrib.get("offset", "")

   def isValid(self):
      return True

   def dumpOnto(self, root):
      if self.val:
         for connNode in root.findall("connection"):
            if connNode.attrib["side"] == "left":
               node = connNode
               break
         else:
            node = ET.Element("connection")
            node.attrib["side"] = "left"
            root.append(node)
         
         node.attrib["offset"] = self.val

class RightConnectionProperty(PropertyView):
   def __init__(self, master):
      PropertyView.__init__(self, master, "Right connection")

   def loadData(self, root):
      for connNode in root.findall("connection"):
         if connNode.attrib["side"] == "right":
            node = connNode
            break
      else:
         self.val = ""
         return

      self.val = node.attrib.get("map", "")

   def isValid(self):
      return True

   def dumpOnto(self, root):
      if self.val:
         for connNode in root.findall("connection"):
            if connNode.attrib["side"] == "right":
               node = connNode
               break
         else:
            node = ET.Element("connection")
            node.attrib["side"] = "right"
            root.append(node)
         
         node.attrib["map"] = self.val
         

class RightOffsetProperty(PropertyView):
   def __init__(self, master):
      PropertyView.__init__(self, master, "Right offset")

   def loadData(self, root):
      for connNode in root.findall("connection"):
         if connNode.attrib["side"] == "right":
            node = connNode
            break
      else:
         self.val = ""
         return

      self.val = node.attrib.get("offset", "")

   def isValid(self):
      return True

   def dumpOnto(self, root):
      if self.val:
         for connNode in root.findall("connection"):
            if connNode.attrib["side"] == "right":
               node = connNode
               break
         else:
            node = ET.Element("connection")
            node.attrib["side"] = "right"
            root.append(node)
         
         node.attrib["offset"] = self.val

class UpConnectionProperty(PropertyView):
   def __init__(self, master):
      PropertyView.__init__(self, master, "Up connection")

   def loadData(self, root):
      for connNode in root.findall("connection"):
         if connNode.attrib["side"] == "up":
            node = connNode
            break
      else:
         self.val = ""
         return

      self.val = node.attrib.get("map", "")

   def isValid(self):
      return True

   def dumpOnto(self, root):
      if self.val:
         for connNode in root.findall("connection"):
            if connNode.attrib["side"] == "up":
               node = connNode
               break
         else:
            node = ET.Element("connection")
            node.attrib["side"] = "up"
            root.append(node)
         
         node.attrib["map"] = self.val
         

class UpOffsetProperty(PropertyView):
   def __init__(self, master):
      PropertyView.__init__(self, master, "Up offset")

   def loadData(self, root):
      for connNode in root.findall("connection"):
         if connNode.attrib["side"] == "up":
            node = connNode
            break
      else:
         self.val = ""
         return

      self.val = node.attrib.get("offset", "")

   def isValid(self):
      return True

   def dumpOnto(self, root):
      if self.val:
         for connNode in root.findall("connection"):
            if connNode.attrib["side"] == "up":
               node = connNode
               break
         else:
            node = ET.Element("connection")
            node.attrib["side"] = "up"
            root.append(node)
         
         node.attrib["offset"] = self.val

class DownConnectionProperty(PropertyView):
   def __init__(self, master):
      PropertyView.__init__(self, master, "Down connection")

   def loadData(self, root):
      for connNode in root.findall("connection"):
         if connNode.attrib["side"] == "down":
            node = connNode
            break
      else:
         self.val = ""
         return

      self.val = node.attrib.get("map", "")

   def isValid(self):
      return True

   def dumpOnto(self, root):
      if self.val:
         for connNode in root.findall("connection"):
            if connNode.attrib["side"] == "down":
               node = connNode
               break
         else:
            node = ET.Element("connection")
            node.attrib["side"] = "down"
            root.append(node)
         
         node.attrib["map"] = self.val
         

class DownOffsetProperty(PropertyView):
   def __init__(self, master):
      PropertyView.__init__(self, master, "Down offset")

   def loadData(self, root):
      for connNode in root.findall("connection"):
         if connNode.attrib["side"] == "down":
            node = connNode
            break
      else:
         self.val = ""
         return

      self.val = node.attrib.get("offset", "")

   def isValid(self):
      return True

   def dumpOnto(self, root):
      if self.val:
         for connNode in root.findall("connection"):
            if connNode.attrib["side"] == "down":
               node = connNode
               break
         else:
            node = ET.Element("connection")
            node.attrib["side"] = "down"
            root.append(node)
         
         node.attrib["offset"] = self.val


