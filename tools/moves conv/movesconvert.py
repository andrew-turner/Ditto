import os
import tkinter.filedialog
import sys, traceback
import xml.etree.ElementTree as ET

try:
   old = tkinter.filedialog.askopenfilename(title="Old moves PBS")
   new = tkinter.filedialog.asksaveasfilename(title="New moves XML")

   root = ET.Element("moves")

   with open(old, "r") as f:
      for line in f:
         vals = line.split(",")
         for v in vals:
            v.strip()

         print(vals[1])
            
         node = ET.SubElement(root, "move")
         node.attrib["id"] = vals[1]
         node.attrib["name"] = vals[2]
         node.attrib["power"] = vals[4]
         node.attrib["type"] = vals[5]
         node.attrib["category"] = vals[6].lower()
         node.attrib["accuracy"] = vals[7]
         node.attrib["pp"] = vals[8]
         node.attrib["target"] = vals[9]
         node.attrib["priority"] = vals[10]
         #node.attrib["description"] = vals[14]

   parser = ET.XMLParser(encoding="utf-8")
   tree = ET.ElementTree(root)
   tree.write(new)

   print("")
   input("Finished!")


except Exception as e:
   print("")
   print("Exception generated!")
   print("-"*20)
   traceback.print_exc(file=sys.stdout)
   print("-"*20)
   input()
