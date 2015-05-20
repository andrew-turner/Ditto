from tkinter import *

NPC_ICON = "assets/npc_add.gif"
WARP_ICON = "assets/warp_add.gif"
SCRIPT_ICON = "assets/script_add.gif"
OBJECT_ICON = "assets/object_add.gif"

class MapObjectPallette(Frame):
   def __init__(self, master):
      Frame.__init__(self, master)
      self.config(relief=RIDGE, bd=2)

      self.icons = {"npc": PhotoImage(file=NPC_ICON),
                    "warp": PhotoImage(file=WARP_ICON),
                    "script": PhotoImage(file=SCRIPT_ICON),
                    "object": PhotoImage(file=OBJECT_ICON)}

      self.npcButton = Button(self, image=self.icons["npc"], width=48, height=48)
      self.npcButton.pack(side=LEFT)

      self.warpButton = Button(self, image=self.icons["warp"], width=48, height=48)
      self.warpButton.pack(side=LEFT)

      self.scriptButton = Button(self, image=self.icons["script"], width=48, height=48)
      self.scriptButton.pack(side=LEFT)

      self.objectButton = Button(self, image=self.icons["object"], width=48, height=48)
      self.objectButton.pack(side=LEFT)

   def bindCreateMethod(self, func):
      self.npcButton.config(command=lambda: func("npc"))
      self.warpButton.config(command=lambda: func("warp"))
      self.scriptButton.config(command=lambda: func("script"))
      self.objectButton.config(command=lambda: func("object"))
