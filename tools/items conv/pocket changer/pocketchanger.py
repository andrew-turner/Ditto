import os
import tkinter.filedialog
import sys, traceback
import xml.etree.ElementTree as ET
import csv

POCKET_MAP = {"1": "ITEMS",
              "2": "MEDECINE",
              "3": "BALLS",
              "4": "TMS",
              "5": "BERRIES",
              "6": "MAIL",
              "7": "BATTLEITEMS",
              "8": "KEYITEMS"}

try:
   old = tkinter.filedialog.askopenfilename(title="Old items XML")
   new = tkinter.filedialog.asksaveasfilename(title="New items XML")

   tree = ET.parse(old)
   root = tree.getroot()
   
   for itemNode in root.findall("item"):
      print(itemNode.attrib["id"])
      oldPocket = itemNode.attrib["pocket"]
      newPocket = POCKET_MAP[oldPocket]
      itemNode.attrib["pocket"] = newPocket
   
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
