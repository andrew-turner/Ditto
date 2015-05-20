from . import ai_1

options = {1: ai_1.AI}

def get(level, battle):
   try:
      cls = options[level]
   except KeyError:
      print("No such AI")
      #raise error
   return cls(battle)
