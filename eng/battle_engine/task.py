import eng.exp

from eng.constants.stats import *

class Task():
   def __init__(self, battle, **kwargs):
      self.battle = battle
      self.kwargs = kwargs

      self.busy = True

   def onStart(self):
      pass

   def tick(self):
      pass

   def onEnd(self):
      pass

class GetPlayerAction(Task):
   def onStart(self):
      print("Getting player action")
      self.battle.activeObject = self.battle.menu
      self.battle.menu.visible = True
      self.battle.dialog.setText("What will$$%s do?" % self.battle.playerPoke.name)

   def onEnd(self):
      self.battle.activeObject = None
      self.battle.menu.visible = False
      self.battle.movemenu.visible = False

class GetEnemyAction(Task):
   def onStart(self):
      print("Getting enemy action")
      self.battle.ai.doAction()
      self.busy = False

class ExecuteMoves(Task):
   def onStart(self):
      print("Sorting moves")
      l = self.battle.selectedMoves
      l.sort(key=lambda a: a[0].stats[ST_SPEED])
      l.sort(key=lambda a: a[2].priority)

      for t in l:
         self.battle.taskMgr.addTasks([ExecuteSingleMove(self.battle),
                                       CheckForFainting(self.battle)])

      self.busy = False

class ExecuteSingleMove(Task):
   def onStart(self):
      print("Executing a move")
      self.tasks = []
      p, t, m = self.battle.selectedMoves.pop()
      self.battle.dialog.setText("%s used %s!" % (p.name, m.name))
      m.use(p, t, self)
      
      self.timer = 0

   def addMessage(self, message, time):
      self.tasks.append(BattleMessage(self.battle, message=message, time=time))

   def tick(self):
      if self.timer == 10:
         self.battle.playerStatusBox.changeHP()
         self.battle.enemyStatusBox.changeHP()
      
      self.timer += 1      
      self.busy = (self.battle.playerStatusBox.changingHP
                   or self.battle.enemyStatusBox.changingHP
                   or (self.timer < 40))

   def onEnd(self):
      self.battle.taskMgr.addTasksToFront(self.tasks)

class BattleMessage(Task):
   def onStart(self):
      self.battle.dialog.setText(self.kwargs["message"])
      self.msgTime = self.kwargs["time"]

      self.timer = 0

   def tick(self):
      self.timer += 1
      self.busy = self.timer < self.msgTime

class CheckForFainting(Task):
   def onStart(self):
      if self.battle.playerPoke.fainted:
         text = "%s fainted!" % self.battle.playerPoke.name
         self.battle.taskMgr.addTasksToFront([BattleMessage(self.battle, message=text, time=30),
                                              ChooseNewPokemon(self.battle)])

      if self.battle.enemyPoke.fainted:
         text = "%s fainted!" % self.battle.enemyPoke.name
         self.battle.taskMgr.addTasksToFront([BattleMessage(self.battle, message=text, time=30),
                                              GainExp(self.battle),
                                              ExitBattle(self.battle)])
   
      self.busy = False

class ChooseNewPokemon(Task):
   def onStart(self):
      self.battle.foregroundObject = menus.PartyScreen(self.battle.screen)

class GainExp(Task):
   def onStart(self):
      gain = exp.getExpGain(self.battle.playerPoke, self.battle.enemyPoke, False)
      
      text = "%s gained %i exp!" % (self.battle.playerPoke.name, gain)
      self.battle.taskMgr.addTasksToFront([BattleMessage(self.battle, message=text, time=30)])

      self.busy = False

class ExitBattle(Task):
   def onStart(self):
      self.battle.busy = False

class Stall(Task):
   def onStart(self):
      print("STALL")
