import eng.data as data

from . import stat_change

EFFECT_NAMES = {"increaseuser": stat_change.IncreaseUser,
                "decreaseuser": stat_change.DecreaseUser,
                "increasetarget": stat_change.IncreaseTarget,
                "decreasetarget": stat_change.DecreaseTarget}

def getEffect(node):
   effectType = node.getAttr("type", data.D_STRING)
   try:
      cls = EFFECT_NAMES[effectType]
   except KeyError:
      raise KeyError #raise an error

   return cls(node)
