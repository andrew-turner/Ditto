import os
import Image
import tkinter.filedialog
import sys, traceback

try:
   olddir = tkinter.filedialog.askdirectory(title="Old dir")
   newdir = tkinter.filedialog.askdirectory(title="New dir")

   names = os.listdir(olddir)

   for name in names:
      im = Image.open(os.path.join(olddir, name))
      im2 = im.resize((80,80))
      im2.save(os.path.join(newdir, name))

   print("Done")

except Exception as e:
   print("")
   print("-"*20)
   traceback.print_exc(file=sys.stdout)
   print("-"*20)

print("")
input("Enter to exit")
