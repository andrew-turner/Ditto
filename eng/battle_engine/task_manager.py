class TaskManager():
   def __init__(self):
      self.currentTask = None
      
      self.taskQueue = []

      self.busy = True

   def addTasks(self, tasks):
      self.taskQueue += tasks

   def addTasksToFront(self, tasks):
      self.taskQueue = tasks + self.taskQueue

   def endCurrentTask(self):
      self.currentTask.busy = False

   def tick(self):
      if self.currentTask is not None:
         self.currentTask.tick()
         if not self.currentTask.busy:
            self.currentTask.onEnd()
            self.currentTask = None

      if self.currentTask is None:
         if self.taskQueue:
            self.currentTask = self.taskQueue.pop(0)
            print(self.currentTask)
            self.currentTask.onStart()
            self.busy = True
         else:
            print("Out of tasks!")
            self.busy = False
