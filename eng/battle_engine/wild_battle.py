from . import base_battle
from . import battle_trainer
from . import wild_pokemon

#screen transition
#pokemon enters from left, trainer from right
#"Wild Donphan appeared!" Wait for A
#"Go Rhyhorn!" Throws out poke, trainer exits left
#"What will Rhyhorn do?" Fight, Bag, Pokemon, Run
#choose attack
#execute battle round, fastest first
#etc


class WildBattle(base_battle.BaseBattle):
   def __init__(self, screen, player, enemy, environment=None, weather=None):
      player = battle_trainer.BattleTrainer(player)
      enemy = wild_pokemon.WildPokemon(enemy)
      
      base_battle.BaseBattle.__init__(self, screen, player, enemy, environment, weather)
