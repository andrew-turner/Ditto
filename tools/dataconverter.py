import os

def getAttrFixer(line):
   com = "data.getAttr("
   start = line.find(com)
   if start == -1:
      return line

   print line

   i1 = start + len(com)
   i2 = line[i1:].find(")") + i1

   nodeName, attrName, formatting = [arg.strip() for arg in line[i1:i2].split(",")]
   
   bits = (line[:start],
           "{node}.getAttr({attr}, {form})".format(node=nodeName,
                                                   attr=attrName,
                                                   form=formatting),
           line[i2+1:])

   new = "".join(bits)

   print "---> {}".format(new)

   return new

def getOptionalAttrFixer(line):
   com = "data.getOptionalAttr("
   start = line.find(com)
   if start == -1:
      return line

   print line.strip()

   i1 = start + len(com)
   i2 = line[i1:].find(")") + i1

   args = [arg.strip() for arg in line[i1:i2].split(",")]
   if len(args) == 3:
      nodeName, attrName, formatting = args
      middle = "{node}.getOptionalAttr({attr}, {form})".format(node=nodeName,
                                                               attr=attrName,
                                                               form=formatting)
   else:
      nodeName, attrName, formatting, default = args
      middle = "{node}.getOptionalAttr({attr}, {form}, {default})".format(node=nodeName,
                                                                          attr=attrName,
                                                                          form=formatting,
                                                                          default=default)
   
   bits = (line[:start],
           middle,
           line[i2+1:])

   new = "".join(bits)

   print "---> {}".format(new.strip())

   return new

def getChildFixer(line):
   com = "data.getChild("
   start = line.find(com)
   if start == -1:
      return line

   print line

   i1 = start + len(com)
   i2 = line[i1:].find(")") + i1

   nodeName, childName = [arg.strip() for arg in line[i1:i2].split(",")]
   
   bits = (line[:start],
           "{node}.getChild({child})".format(node=nodeName,
                                             child=childName),
           line[i2+1:])

   new = "".join(bits)

   print "---> {}".format(new)

   return new

def getChildrenFixer(line):
   com = "data.getChildren("
   start = line.find(com)
   if start == -1:
      return line

   print line.strip()

   i1 = start + len(com)
   i2 = line[i1:].find(")") + i1

   args = [arg.strip() for arg in line[i1:i2].split(",")]
   if len(args) == 1:
      nodeName = args[0]
      middle = "{node}.getChildren()".format(node=nodeName)
   else:
      nodeName, childName = args
      middle = "{node}.getChildren({child})".format(node=nodeName,
                                                    child=childName)
   
   bits = (line[:start],
           middle,
           line[i2+1:])

   new = "".join(bits)

   print "---> {}".format(new.strip())

   return new

FIXERS = (getAttrFixer,
          getOptionalAttrFixer,
          getChildFixer,
          getChildrenFixer)

def fix(fn):
   newLines = []
   with open(fn) as f:
      for line in f.readlines():
         res = line
         for fixer in FIXERS:
            res = fixer(res)
         newLines.append(res)
   with open(fn, "w") as newF:
      newF.writelines(newLines)
   return

def fixFolder(path):
   for fn in os.listdir(path):
      full = os.path.join(path, fn)
      if os.path.isdir(full):
         fixFolder(full)
      elif os.path.splitext(full)[1] == ".py":
         print "----------"
         print full
         print "----------"
         fix(full)
      
            

if __name__ == "__main__":
   folder = None #".\\eng"
   fixFolder(folder)
   try:
      input()
   except:
      pass
