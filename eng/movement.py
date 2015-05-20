#define move permission constants
#move permission is taken mod 8 to see what style it is
SWITCH = 0
BLOCK = 1
CLEAR = 2
BRIDGE = 3
TERRAIN = 4
LEDGE = 5

def getAction(i):
   return i%8

def getLevel(i):
   return int(i//8)-1

def getActionLevel(i):
   return (getAction(i),
           getLevel(i))
