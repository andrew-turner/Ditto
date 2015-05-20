import os

import eng.foreground_object as foreground_object
import eng.game_input
import eng.data
import eng.settings
import eng.globs
import eng.font
from . import status_box
from . import battle_dialog
from . import battle_menu
from . import move_menu
from . import task
from . import task_manager
from . import ai

#BaseBattle object
#

#actors
A_PLAYER = 0
A_ENEMY = 1

class BaseBattle(foreground_object.ForegroundObject):
   def __init__(self, screen, player, enemy, environment, weather):
      self.screen = screen

      self.player = player
      self.enemy = enemy

      root = data.getTreeRoot(os.path.join(settings.path, "data", globs.BATTLE), "Battle global")
      transparency = root.getAttr("transparency", data.D_INT3LIST)

      #load battle background
      self.environment = environment
      environmentsNode = root.getChild("environments")
      for environmentNode in environmentsNode.getChildren("environment"):
         if environmentNode.getAttr("id", data.D_STRING) == self.environment:
            fn = environmentNode.getAttr("file", data.D_STRING)
            break
      else:
         #raise error
         pass

      self.back = data.getImage(os.path.join(settings.path, "data", fn), root.ditto_fn)
      self.screenLocation = ((self.screen.get_width()-self.back.get_width())/2,
                             (self.screen.get_height()-self.back.get_height())/2)
      self.width = self.back.get_width()
      self.height = self.back.get_height()

      #load pokemon
      self.enemyPoke = self.enemy.getActivePoke()
      self.playerPoke = self.player.getActivePoke()

      #load status boxes
      self.playerStatusBox = status_box.PlayerStatusBox(screen, root, self.playerPoke)
      self.playerStatusBox.setLocation((150,100), self.screenLocation)
      self.enemyStatusBox = status_box.EnemyStatusBox(screen, root, self.enemyPoke)
      self.enemyStatusBox.setLocation((10,10), self.screenLocation)
      
      #create AI
      self.ai = ai.get(1, self)

      #create objects
      self.dialog = battle_dialog.BattleDialog(screen, root.getChild("battledialog"), self.width)
      self.dialog.setLocation((0, self.height-self.dialog.height), self.screenLocation)

      self.menu = battle_menu.BattleMenu(screen, root.getChild("battlemenu"), self)
      self.menu.setLocation((self.width/2, 0), self.dialog.location)
      self.menu.callbacks[battle_menu.BC_FIGHT] = self.battle_fight
      self.menu.callbacks[battle_menu.BC_RUN] = self.battle_run

      self.movemenu = move_menu.MoveMenu(screen, root.getChild("movemenu"), self)
      self.movemenu.setLocation((0,0), self.dialog.location)
      self.movemenu.callbacks[move_menu.MC_MOVE] = self.move_useMove
      self.movemenu.callbacks[move_menu.MC_CANCEL] = self.move_cancel

      self.foregroundObject = None
      self.activeObject = None
      self.busy = True
      self.isOver = False

      self.selectedMoves = []

      self.taskMgr = task_manager.TaskManager()

   def selectMove(self, poke, target, index):
      self.selectedMoves.append((poke, target, poke.moves[index]))

   def battle_fight(self):
      self.activeObject = self.movemenu
      self.menu.visible = False
      self.movemenu.visible = True

   def battle_run(self):
      self.busy = False

   def move_useMove(self, index):
      self.taskMgr.endCurrentTask()
      self.selectMove(self.playerPoke, self.enemyPoke, index)

   def move_cancel(self):
      self.activeObject = self.menu
      self.movemenu.visible = False
      self.menu.visible = True

   def inputButton(self, button):
      if self.activeObject is not None:
         self.activeObject.inputButton(button)

   def draw(self):
      if self.foregroundObject is not None:
         self.foregroundObject.draw()
         
      self.screen.fill((255,255,0))

      self.screen.blit(self.back, self.screenLocation)

      im = self.enemyPoke.getFrontBattler()
      self.screen.blit(im, (self.screenLocation[0]+130, self.screenLocation[1]+10))
      im = self.playerPoke.getBackBattler()
      self.screen.blit(im, (self.screenLocation[0]+50, self.screenLocation[1]+50))

      self.playerStatusBox.draw()
      self.enemyStatusBox.draw()

      if self.dialog is not None:
         self.dialog.draw()
      if self.menu is not None:
         self.menu.draw()
      if self.movemenu is not None:
         self.movemenu.draw()

   def tick(self):
      self.taskMgr.tick()
      if not self.taskMgr.busy:
         if not self.isOver:
            self.taskMgr.addTasks([task.GetPlayerAction(self),
                                   task.GetEnemyAction(self),
                                   task.ExecuteMoves(self)])
         else:
            self.busy = False
      
      self.playerStatusBox.tick()
      self.enemyStatusBox.tick()

      self.dialog.tick()


      
      

   
      
