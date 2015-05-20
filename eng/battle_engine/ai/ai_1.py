import random

class AI():
   def __init__(self, battle):
      self.battle = battle

   def doAction(self):
      self.battle.selectMove(self.battle.enemyPoke, self.battle.playerPoke, random.randint(0,3))
