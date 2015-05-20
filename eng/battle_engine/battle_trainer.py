from . import battle_pokemon

class BattleTrainer():
   def __init__(self, trainer):
      self.trainer = trainer

      self.party = []
      for p in self.trainer.party:
         self.party.append(battle_pokemon.BattlePokemon(p))

      self.activePoke = 0

   def getActivePoke(self):
      return self.party[self.activePoke]
