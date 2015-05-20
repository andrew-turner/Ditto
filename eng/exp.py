#exp formulas as given by Bulbapedia

GEN5_FORMULA = True

def getExpGain(victor, defeated, isTrainer=False):
   #trainer
   trainer = 1.5 if isTrainer else 1.0

   #traded
   traded = 1

   #base exp
   baseExp = defeated.baseExp

   #lucky egg
   egg = 1

   #levels
   levelVictor = victor.level
   levelDefeated = defeated.level

   #exp share
   share = 1

   #exp point power
   power = 1
   
   if GEN5_FORMULA:
      first = (trainer*baseExp*levelDefeated)/(5*share)
      second = (((2*levelDefeated)+10)**2.5)/((levelDefeated+levelVictor+10)**2.5)

      block = (first*second)+1

      return int(block*traded*egg*power)
   
   else:
      return 1
