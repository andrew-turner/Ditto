#! python3

from PIL import Image
import tkinter.filedialog

tileSize = input("Tilesize: ")
tileSize = list(map(int, tileSize.split(",")))

source = Image.open(tkinter.filedialog.askopenfilename())

tiles = int(source.size[0]//tileSize[0]), int(source.size[1]//tileSize[1])

result = Image.new("RGB", (source.size[0]+tiles[0]-1, source.size[1]+tiles[1]-1), (0,255,255))

for x in range(0, tiles[0]):
   for y in range(0, tiles[1]):
      t = source.crop((x*tileSize[0], y*tileSize[1], (x+1)*tileSize[0], (y+1)*tileSize[1]))
      result.paste(t, ((x*(tileSize[0]+1)), (y*(tileSize[1]+1))))

result.save(tkinter.filedialog.asksaveasfilename())
