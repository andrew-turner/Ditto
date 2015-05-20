import os
import tkinter.filedialog
import sys, traceback
import xml.etree.ElementTree as ET
import csv

try:
   old = tkinter.filedialog.askopenfilename(title="Old items PBS")
   new = tkinter.filedialog.asksaveasfilename(title="New items XML")

   root = ET.Element("items")

   with open(old, "r") as f:
      r = csv.reader(f)
      for row in r:
         for val in row:
            val.strip()

         print(row[1])
            
         node = ET.SubElement(root, "item")
         node.attrib["id"] = row[1]
         node.attrib["name"] = row[2]
         node.attrib["pocket"] = row[3]
         node.attrib["price"] = row[4]
         node.attrib["description"] = row[5]

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
