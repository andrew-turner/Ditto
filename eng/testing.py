import time

from . import pokemon

def timeFunction(func, args=None):
   if args is None:
      args = []
   print("-- Starting testing --")
   t1 = time.clock()
   func(*args)
   t2 = time.clock()
   print("-- Finished testing --")
   print("Function took %f secs to execute" % (t2-t1))

def testExp():
   for rate in ["Fast", "Medium", "Slow", "Parabolic", "Erratic", "Fluctuating"]:
      print("-"*10)
      print(rate)
      print("-"*10)
      for n in range(0, 100):
         print("%i: %i" % (n, pokemon.expAtLevel(n, rate)))
      input(rate)

if __name__ == "__main__":
   testExp()
