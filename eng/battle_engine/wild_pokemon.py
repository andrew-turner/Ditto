from . import battle_pokemon

class WildPokemon():
   def __init__(self, poke):
      self.poke = battle_pokemon.BattlePokemon(poke)

   def getActivePoke(self):
      return self.poke
