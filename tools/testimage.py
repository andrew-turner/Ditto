import os
import Image
import tkinter.filedialog
import sys, traceback

try:
   fn = tkinter.filedialog.askopenfilename()
   im = Image.open(fn)
   im.convert("RGBA")

   channels = im.split()
   for c in channels:
      print(c)
      
   input()

except Exception as e:
   print("")
   print("Exception generated!")
   print("-"*20)
   traceback.print_exc(file=sys.stdout)
   print("-"*20)
   input()
