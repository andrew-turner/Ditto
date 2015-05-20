import wx
import sys, traceback
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

def getAttr(node, att):
   if att in node.attrib:
      return node.attrib[att]
   else:
      return ""

def checkNode(node):
   names = ["type", "basestats", "gender", "growth", "defeat", "catch", "attacks", "egg", "dex", "ability", "graphics"]

   for name in names:
      if node.find(name) is None:
         ET.SubElement(node, name)

class AttribEntry(wx.TextCtrl):
   def __init__(self, master, att):
      wx.TextCtrl.__init__(self, master)

      self.att = att

class Editor(wx.Frame):
   def __init__(self, parent, title):
      wx.Frame.__init__(self, parent, title=title)

      filemenu = wx.Menu()
      menuSave = filemenu.Append(wx.ID_ANY, "&Save", "Save")
      menuAbout = filemenu.Append(wx.ID_ABOUT, "&About", "Info")
      menuExit = filemenu.Append(wx.ID_EXIT, "E&xit", "Terminate")

      menuBar = wx.MenuBar()
      menuBar.Append(filemenu, "&File")
      self.SetMenuBar(menuBar)

      self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
      self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
      self.Bind(wx.EVT_MENU, self.OnSave, menuSave)

      dirname = ""
      dlg = wx.FileDialog(self, "Open file", dirname, "", "*.xml", wx.OPEN)
      if dlg.ShowModal() == wx.ID_OK:
         self.filename = dlg.GetFilename()
         self.dirname = dlg.GetDirectory()
         self.tree = ET.parse(os.path.join(self.dirname, self.filename))
         self.root = self.tree.getroot()
         self.speciesList = [sp.attrib["id"] for sp in self.root.findall("species")]
            
      dlg.Destroy()

      self.scroll = wx.ScrolledWindow(self)
      self.scroll.SetVirtualSize((400,600))
      self.scroll.SetScrollRate(20,20)

      self.choose = wx.ComboBox(self.scroll, choices=self.speciesList, style=wx.CB_READONLY)
      self.Bind(wx.EVT_COMBOBOX, self.EvtComboBox, self.choose)

      b = wx.Button(self.scroll, wx.ID_ADD, "New Pokemon")
      self.Bind(wx.EVT_BUTTON, self.OnAddPoke, b)

      self.sizer = wx.BoxSizer(wx.VERTICAL)
      topsizer = wx.BoxSizer(wx.HORIZONTAL)
      topsizer.Add(self.choose, 4)
      topsizer.Add(b, 1)
      self.sizer.Add(topsizer, 1, wx.EXPAND)

      self.currentSizer = wx.BoxSizer(wx.VERTICAL)

      self.speciesNode = self.root.find("species")

      self.order = ["ID", "Name", "Dex no.", "Primary type", "Secondary type", "HP", "Attack", "Defense", "Sp Attack", "Sp Defense", "Speed", "Gender rate", "Growth rate",
                    "Base exp", "HP EVs", "Attack EVs", "Defense EVs", "Sp Attack EVs", "Sp Defense EVs", "Speed EVs", "Catch rate", "Egg groups", "Hatch steps", "Height", "Weight",
                    "Color", "Kind", "Dex entry", "Abilities", "Hidden abilities"]

      self.textboxes = {}
      for att in self.order:
         sizer = wx.BoxSizer(wx.HORIZONTAL)
         label = wx.StaticText(self.scroll, label=att)
         textbox = AttribEntry(self.scroll, att)
         textbox.Bind(wx.EVT_KILL_FOCUS, self.EvtTextCtrl)
         sizer.Add(label, 1, wx.EXPAND)
         sizer.Add(textbox, 1, wx.EXPAND)
         self.textboxes[att] = textbox
         self.currentSizer.Add(sizer, 1, wx.EXPAND)

      self.loadPoke()

      self.sizer.Add(self.currentSizer, 15, wx.EXPAND)

      #self.scroll.SetAutoLayout(True)
      self.scroll.SetSizer(self.sizer)
      self.sizer.Fit(self.scroll)

      self.Show(True)

   def loadPoke(self):
      checkNode(self.speciesNode)
      
      self.attribs = {"ID": (self.speciesNode, "id"),
                      "Name": (self.speciesNode, "name"),
                      "Dex no.": (self.speciesNode, "dex"),
                      "Primary type": (self.speciesNode.find("type"), "primary"),
                      "Secondary type": (self.speciesNode.find("type"), "secondary"),
                      "HP": (self.speciesNode.find("basestats"), "hp"),
                      "Attack": (self.speciesNode.find("basestats"), "attack"),
                      "Defense": (self.speciesNode.find("basestats"), "defense"),
                      "Sp Attack": (self.speciesNode.find("basestats"), "spatk"),
                      "Sp Defense": (self.speciesNode.find("basestats"), "spdef"),
                      "Speed": (self.speciesNode.find("basestats"), "speed"),
                      "Gender rate": (self.speciesNode.find("gender"), "rate"),
                      "Growth rate": (self.speciesNode.find("growth"), "rate"),
                      "Base exp": (self.speciesNode.find("defeat"), "exp"),
                      "HP EVs": (self.speciesNode.find("defeat"), "hpev"),
                      "Attack EVs": (self.speciesNode.find("defeat"), "attackev"),
                      "Defense EVs": (self.speciesNode.find("defeat"), "defenseev"),
                      "Sp Attack EVs": (self.speciesNode.find("defeat"), "spatkev"),
                      "Sp Defense EVs": (self.speciesNode.find("defeat"), "spdefev"),
                      "Speed EVs": (self.speciesNode.find("defeat"), "speedev"),
                      "Catch rate": (self.speciesNode.find("catch"), "rate"),
                      "Egg groups": (self.speciesNode.find("egg"), "group"),
                      "Hatch steps": (self.speciesNode.find("egg"), "steps"),
                      "Height": (self.speciesNode.find("dex"), "height"),
                      "Weight": (self.speciesNode.find("dex"), "weight"),
                      "Color": (self.speciesNode.find("dex"), "color"),
                      "Kind": (self.speciesNode.find("dex"), "kind"),
                      "Dex entry": (self.speciesNode.find("dex"), "entry"),
                      "Abilities": (self.speciesNode.find("ability"), "main"),
                      "Hidden abilities": (self.speciesNode.find("ability"), "hidden")}
                      
                      
                     

   #["ID", "Name", "Dex no.", "Primary type", "Secondary type", "HP", "Attack", "Defense", "Sp Attack", "Sp Defense", "Speed", "% Male", "% Female", "Growth rate",
   #"Base exp", "HP EVs", "Attack EVs", "Defense EVs", "Sp Attack EVs", "Sp Defense EVs", "Speed EVs", "Catch rate", "Egg groups", "Hatch steps", "Height", "Weight",
   #"Color", "Kind", "Dex entry", "Abilities", "Hidden abilitis"]
      for att in self.order:
         a = self.attribs[att]
         self.textboxes[att].SetValue(getAttr(a[0], a[1]))

   def OnSave(self, e):
      dirname = ""
      dlg = wx.FileDialog(self, "Save file", dirname, "", "*.xml", wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
      if dlg.ShowModal() == wx.ID_OK:
         filename = dlg.GetFilename()
         dirname = dlg.GetDirectory()

         self.tree.write(os.path.join(dirname, filename))
         
            
      dlg.Destroy()

   def OnAbout(self, e):
      dlg = wx.MessageDialog(self, "Pokemon editor for Ditto.", "About", wx.OK)
      dlg.ShowModal()
      dlg.Destroy()

   def OnExit(self, e):
      self.Close(True)

   def OnAddPoke(self, e):
      self.speciesNode = ET.SubElement(self.root, "species")
      self.speciesNode.attrib["id"] = "NEWPOKEMON"

      self.loadPoke()

   def EvtComboBox(self, e):      
      choice = self.choose.GetValue()

      if self.speciesNode.attrib["id"] == "NEWPOKEMON":
         dlg = wx.MessageDialog(self, "Please enter pokemon ID.", "Problem", wx.OK)
         dlg.ShowModal()
         dlg.Destroy()
      else:
         if not (self.speciesNode.attrib["id"] in self.speciesList):
            self.speciesList.append(self.speciesNode.attrib["id"])
            self.choose.Append(self.speciesNode.attrib["id"])
         
         for sp in self.root.findall("species"):
            if sp.attrib["id"] == choice:
               self.speciesNode = sp

         self.loadPoke()

   def EvtTextCtrl(self, e):
      o = e.GetEventObject()
      node, attrib = self.attribs[o.att]

      node.attrib[attrib] = o.GetValue()

      
         
         
      
try:
   app = wx.App(False)
   main = Editor(None, "Editor")
   app.MainLoop()
   
except Exception as e:
   print("")
   print("Exception generated!")
   print("-"*20)
   traceback.print_exc(file=sys.stdout)
   print("-"*20)
   input()

