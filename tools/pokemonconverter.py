import configparser
import tkinter.filedialog
import xml.etree.ElementTree as ET
import sys, traceback

try:
   openfn = tkinter.filedialog.askopenfilename()

   #icondir = tkFileDialog.askdirectory("Icon dir")

   conf = configparser.RawConfigParser()
   conf.read(openfn)

   root = ET.Element("pokemon")

   eggGroups = {"1": "MONSTER",
                "2": "WATER1",
                "3": "BUG",
                "4": "FLYING",
                "5": "GROUND",
                "6": "FAIRY",
                "7": "PLANT",
                "8": "HUMANLIKE",
                "9": "WATER3",
                "10": "MINERAL",
                "11": "AMORPHOUS",
                "12": "WATER2",
                "13": "DITTO",
                "14": "DRAGON",
                "15": "NOBREED"}

   for s in conf.sections():
      print(conf.get(s, "InternalName"))
      speciesNode = ET.SubElement(root, "species")
      speciesNode.attrib["id"] = conf.get(s, "InternalName")
      speciesNode.attrib["name"] = conf.get(s, "Name")
      speciesNode.attrib["dex"] = s

      node = ET.SubElement(speciesNode, "type")
      node.attrib["primary"] = conf.get(s, "Type1")
      if conf.has_option(s, "Type2"):
         node.attrib["secondary"] = conf.get(s, "Type2")

      node = ET.SubElement(speciesNode, "basestats")
      stats = conf.get(s, "BaseStats").split(",")
      node.attrib["hp"] = stats[0]
      node.attrib["attack"] = stats[1]
      node.attrib["defense"] = stats[2]
      node.attrib["spatk"] = stats[4]
      node.attrib["spdef"] = stats[5]
      node.attrib["speed"] = stats[3]

      node = ET.SubElement(speciesNode, "gender")
      node.attrib["rate"] = conf.get(s, "GenderRate")

      node = ET.SubElement(speciesNode, "growth")
      node.attrib["rate"] = conf.get(s, "GrowthRate")

      node = ET.SubElement(speciesNode, "defeat")
      node.attrib["exp"] = conf.get(s, "BaseEXP")
      evs = conf.get(s, "EffortPoints").split(",")
      if evs[0] != "0":
         node.attrib["hpev"] = evs[0]
      if evs[1] != "0":
         node.attrib["attackev"] = evs[1]
      if evs[2] != "0":
         node.attrib["defenseev"] = evs[2]
      if evs[4] != "0":
         node.attrib["spatkev"] = evs[4]
      if evs[5] != "0":
         node.attrib["spdefev"] = evs[5]
      if evs[3] != "0":
         node.attrib["speedev"] = evs[3]

      node = ET.SubElement(speciesNode, "catch")
      node.attrib["rate"] = conf.get(s, "Rareness")

      node = ET.SubElement(speciesNode, "attacks")
      data = [m.strip() for m in conf.get(s, "Moves").split(",")]
      numMoves = len(data)/2
      for i in range(0, numMoves):
         moveNode = ET.SubElement(node, "move")
         moveNode.attrib["id"] = data[(i*2)+1]
         moveNode.attrib["level"] = data[i*2]

      node = ET.SubElement(speciesNode, "egg")
      groups = conf.get(s, "Compatibility").split(",")
      names = [eggGroups[g] for g in groups]
      node.attrib["group"] = ",".join(names)
      node.attrib["steps"] = conf.get(s, "StepsToHatch")

      node = ET.SubElement(speciesNode, "dex")
      node.attrib["height"] = conf.get(s, "Height")
      node.attrib["weight"] = conf.get(s, "Weight")
      node.attrib["color"] = conf.get(s, "Color").upper()
      node.attrib["kind"] = conf.get(s, "Kind")
      node.attrib["entry"] = conf.get(s, "Pokedex")

      data = conf.get(s, "Evolutions").split(",")
      numEvos = len(data)/3
      for i in range(0, numEvos):
         node = ET.SubElement(speciesNode, "evolution")
         node.attrib["species"] = data[i*3]
         node.attrib["method"] = data[(i*3)+1].lower()
         node.attrib["level"] = data[(i*3)+2]

      node = ET.SubElement(speciesNode, "ability")
      node.attrib["main"] = conf.get(s, "Abilities")
      if conf.has_option(s, "HiddenAbility"):
         node.attrib["hidden"] = conf.get(s, "HiddenAbility")
      else:
         node.attrib["hidden"] = ""

      node = ET.SubElement(speciesNode, "graphics")
      battleNode = ET.SubElement(node, "battle")
      battleNode.attrib["back"] = "pokemon\\battlers\\%s_b.bmp" % str(s).zfill(3)
      battleNode.attrib["front"] = "pokemon\\battlers\\%s.bmp" % str(s).zfill(3)
      battleNode.attrib["transparency"] = "250,0,250"
      iconNode = ET.SubElement(node, "icon")
      iconNode.attrib["file"] = "pokemon\icons\%s.bmp" % str(s).zfill(3)
      iconNode.attrib["size"] = "22,19"
      iconNode.attrib["transparency"] = "250,0,250"
      
   tree = ET.ElementTree(root)

   closefn = tkinter.filedialog.asksaveasfilename()
   tree.write(closefn)
   
except Exception as e:
   print("")
   print("Exception generated!")
   print("-"*20)
   traceback.print_exc(file=sys.stdout)
   print("-"*20)
   input()
