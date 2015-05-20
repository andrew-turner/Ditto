from . import move_effect
import eng.data as data

INC_MESSAGES = {1: "%s's %s increased!",
                2: "%s's %s greatly increased!",
                3: "%s's %s massively increased!",
                -1: "%s's %s won't go any higher!"}

DEC_MESSAGES = {1: "%s's %s decreased!",
                2: "%s's %s greatly decreased!",
                3: "%s's %s massively decreased!",
                -1: "%s's %s won't go any lower!"}


class IncreaseUser(move_effect.MoveEffect):
   def __init__(self, node):
      move_effect.MoveEffect.__init__(self, node)
      
      self.statName = node.getAttr("stat", data.D_STRING)
      try:
         self.stat = move_effect.STAT_NAMES[self.statName]
      except KeyError:
         print(self.statName)
         pass #raise error
      self.amount = node.getAttr("amount", data.D_INT)

   def activate(self, user, target, task):
      success = user.modifiers.increase(self.stat, self.amount)
      if success:
         task.addMessage(INC_MESSAGES[self.amount] % (user.name, move_effect.BATTLE_NAMES[self.stat]), 30)
      else:
         task.addMessage(INC_MESSAGES[-1] % (user.name, move_effect.BATTLE_NAMES[self.stat]), 30)

class DecreaseUser(move_effect.MoveEffect):
   def __init__(self, node):
      self.statName = node.getAttr("stat", data.D_STRING)
      try:
         self.stat = STAT_NAMES[self.statName]
      except KeyError:
         pass #raise error
      self.amount = node.getAttr("amount", data.D_INT)

   def activate(self, user, target, task):
      success = user.modifiers.decrease(self.stat, self.amount)
      if success:
         task.addMessage("%s's %s decreased!" % (user.name, self.statName), 30)
      else:
         task.addMessage("%s's %s won't go any lower!" % (user.name, self.statName), 30)

class IncreaseTarget(move_effect.MoveEffect):
   def __init__(self, node):
      self.statName = node.getAttr("stat", data.D_STRING)
      try:
         self.stat = STAT_NAMES[self.statName]
      except KeyError:
         pass #raise error
      self.amount = node.getAttr("amount", data.D_INT)

   def activate(self, user, target, task):
      success = target.modifiers.increase(self.stat, self.amount)
      if success:
         task.addMessage("%s's %s greatly increased!" % (target.name, self.statName), 30)
      else:
         task.addMessage("%s's %s won't go any higher!" % (target.name, self.statName), 30)

class DecreaseTarget(move_effect.MoveEffect):
   def __init__(self, node):
      self.statName = node.getAttr("stat", data.D_STRING)
      try:
         self.stat = STAT_NAMES[self.statName]
      except KeyError:
         pass #raise error
      self.amount = node.getAttr("amount", data.D_INT)

   def activate(self, user, target, task):
      success = target.modifiers.decrease(self.stat, self.amount)
      if success:
         task.addMessage("%s's %s decreased!" % (target.name, self.statName), 30)
      else:
         task.addMessage("%s's %s won't go any lower!" % (user.name, self.statName), 30)
