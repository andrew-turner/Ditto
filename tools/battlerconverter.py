import os
import Image
import tkinter.filedialog
import sys, traceback
import xml.etree.ElementTree as ET

try:
   olddir = tkinter.filedialog.askdirectory(title="Old dir")
   newdir = tkinter.filedialog.askdirectory(title="New dir")

   fn = tkinter.filedialog.askopenfile()
   tree = ET.parse(fn)
   root = tree.getroot()

   iddict = {}
   for speciesNode in root.findall("species"):
      iddict[int(speciesNode.attrib["dex"])] = speciesNode.attrib["id"]

   names = os.listdir(olddir)

   i = 0
   for name in names:
      idno = name[:-4]
      im = Image.open(os.path.join(olddir, name))
      im2 = im.resize((80,80))

      if len(idno) == 3:
         print(iddict[int(idno)])
         newname = "%s.png" % iddict[int(idno)]
      else:
         newname = "%s_%s.png" % (iddict[int(idno[:3])], idno[3:])
         
      im2.save(os.path.join(newdir, newname))

      i += 1

   input("DONE!")

except Exception as e:
   print("")
   print("Exception generated!")
   print("-"*20)
   traceback.print_exc(file=sys.stdout)
   print("-"*20)
   input()
   
