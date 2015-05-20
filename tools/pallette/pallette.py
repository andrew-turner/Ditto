import sys
import traceback
import functools

from tkinter import *
import tkinter.colorchooser
import tkinter.filedialog
import tkinter.messagebox
import Image
import ImageTk

def myfunc(event):
   print("X")

class app():
   def __init__(self, master):
      self.master = master

      print("C")

      self.fn = tkinter.filedialog.askopenfilename()
      try:
         self.im = Image.open(self.fn)
      except IOError:
         tkinter.messagebox.showerror("Error", "Unable to open image: %s" % self.fn)
         sys.exit()
         return

      self.imageFrame = Frame(self.master)

      self.canvas = Canvas(self.imageFrame)
      self.canvas.config(bg="white",
                         width=self.im.size[0],
                         height=self.im.size[1])
      self.canvas.bind("<Button-1>", self.onCanvasClick)
      self.canvas.pack(side=TOP)

      b = Button(self.imageFrame,
                 text="Save",
                 command=self.save)
      b.pack(side=TOP)

      self.imageFrame.pack(side=LEFT)

      self.coloursFrame = Frame(self.master)

      self.buttons = {}
      cols = getColours(self.im)
      if len(cols) > 50:
         l = Label(self.coloursFrame, text="Too many colours (%i)." % len(cols))
         l.grid()
      else:
         row = 0
         column = 0
         for col in cols:
            b = Button(self.coloursFrame,
                       text=str(col),
                       background=convertColourString(col),
                       command=functools.partial(self.swapColour, col))
            self.buttons[col] = b
            b.grid(row=row, column=column, sticky=W+E)
            row += 1
            if row > 10:
               row = 0
               column += 1

      self.coloursFrame.pack(side=LEFT)

      self.updateCanvas()

   def updateCanvas(self):
      self.tkIm = ImageTk.PhotoImage(self.im)
      self.canvas.create_image(1, 1, image=self.tkIm, anchor=NW)

   def swapColour(self, col):
      colTuple, colString = tkinter.colorchooser.askcolor(col)
      if colString is not None:
         b = self.buttons[col]
         b.config(background=colString,
                  text=str(colTuple),
                  command=functools.partial(self.swapColour, colTuple))
         del self.buttons[col]
         self.buttons[colTuple] = b
         new = replaceColour(self.im, col, colTuple)
         self.im = new
         self.updateCanvas()

   def save(self):
      fn = tkinter.filedialog.asksaveasfilename(initialfile=self.fn)
      if fn is not None:
         self.fn = fn
         self.im.save(fn)

   def onCanvasClick(self, event):
      pos = event.x, event.y
      try:
         col = self.im.getpixel(pos)
      except IndexError:
         return

      self.swapColour(col)
      

def convertColourString(col):
   return "#%02x%02x%02x" % col

def getColours(im):
   ans = []

   pix = im.load()

   for x in range(0, im.size[0]):
      for y in range(0, im.size[1]):
         col = pix[x,y]
         if not col in ans:
            ans.append(col)

   return ans

def replaceColour(im, oldCol, newCol):
   pix = im.load()

   for x in range(0, im.size[0]):
      for y in range(0, im.size[1]):
         if pix[x,y] == oldCol:
            pix[x,y] = newCol

   return im

if __name__ == "__main__":
   try:
      root = Tk()
      myApp = app(root)
      root.mainloop()
   except Exception:
      print("Python exception generated!")
      print("-"*20)
      traceback.print_exc(file=sys.stdout)
      print("-"*20)
      input()







   

   
