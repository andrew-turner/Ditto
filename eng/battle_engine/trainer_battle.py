from . import base_battle

class TrainerBattle(base_battle.BaseBattle):
   def __init__(self, screen, player, opponent):
      self.player = player
      self.opponent = opponent

      self.enemyActivePoke = 0
      
      base_battle.BaseBattle.__init__(self, screen)

   def getEnemyPoke(self):
      return self.opponent.party[self.enemyActivePoke]
