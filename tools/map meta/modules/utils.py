import os

from PIL import Image

def getGameDir(fn):
   body = fn
   tail = ""
   while True:
      body, tail = os.path.split(body)
      if tail == "data":
         return body
      elif tail == "":
         return False

def convertTransparency(im, transparency):
   imA = im.convert("RGBA")
   data = imA.getdata()

   newData = []
   for item in data:
      if ((item[0] == transparency[0]) and
          (item[1] == transparency[1]) and
          (item[1] == transparency[1])):
         newData.append((255,255,255,0))
      else:
         newData.append(item)

   imA.putdata(newData)

   return imA
