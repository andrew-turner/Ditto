import xml.etree.ElementTree as ET

from modules.property_view import PropertyView

class NWProperty(PropertyView):
   def __init__(self, master):
      PropertyView.__init__(self, master, "NW")

   def loadData(self, root):
      borderNode = root.find("border")
      if borderNode is not None:
         self.val = borderNode.attrib.get("nw", "")
      else:
         self.val = ""

   def isValid(self):
      return True

   def dumpOnto(self, root):
      borderNode = root.find("border")
      if borderNode is None:
         borderNode = ET.Element("border")
         root.append(borderNode)

      borderNode.attrib["nw"] = self.val

class NEProperty(PropertyView):
   def __init__(self, master):
      PropertyView.__init__(self, master, "NE")

   def loadData(self, root):
      borderNode = root.find("border")
      if borderNode is not None:
         self.val = borderNode.attrib.get("ne", "")
      else:
         self.val = ""

   def isValid(self):
      return True

   def dumpOnto(self, root):
      borderNode = root.find("border")
      if borderNode is None:
         borderNode = ET.Element("border")
         root.append(borderNode)

      borderNode.attrib["ne"] = self.val

class SWProperty(PropertyView):
   def __init__(self, master):
      PropertyView.__init__(self, master, "SW")

   def loadData(self, root):
      borderNode = root.find("border")
      if borderNode is not None:
         self.val = borderNode.attrib.get("sw", "")
      else:
         self.val = ""

   def isValid(self):
      return True

   def dumpOnto(self, root):
      borderNode = root.find("border")
      if borderNode is None:
         borderNode = ET.Element("border")
         root.append(borderNode)

      borderNode.attrib["sw"] = self.val

class SEProperty(PropertyView):
   def __init__(self, master):
      PropertyView.__init__(self, master, "SE")

   def loadData(self, root):
      borderNode = root.find("border")
      if borderNode is not None:
         self.val = borderNode.attrib.get("se", "")
      else:
         self.val = ""

   def isValid(self):
      return True

   def dumpOnto(self, root):
      borderNode = root.find("border")
      if borderNode is None:
         borderNode = ET.Element("border")
         root.append(borderNode)

      borderNode.attrib["se"] = self.val
