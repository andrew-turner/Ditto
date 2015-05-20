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
      idno =  name[4:-4]
      print(idno)
      im = Image.open(os.path.join(olddir, name))
      #im.convert("RGB")
      newsize = im.size[0]/2, im.size[1]/2
      im.resize(newsize)

      channels = im.split()
      r = channels[0]
      g = channels[1]
      b = channels[2]

      pixR = r.load()
      pixG = g.load()
      pixB = b.load()

      print(pixR[0,0], pixG[0,0], pixB[0,0])

      del pixR
      del pixG
      del pixB

      im = Image.merge("RGB", (r,g,b))

      if len(idno) == 3:
         newname = "%s.bmp" % iddict[int(idno)]
      else:
         newname = "%s%s.bmp" % (iddict[int(idno[:3])], idno[3:])
      im.save(os.path.join(newdir, newname))

      i += 1

   input()

except Exception as e:
   print("")
   print("Exception generated!")
   print("-"*20)
   traceback.print_exc(file=sys.stdout)
   print("-"*20)
   input()
   
