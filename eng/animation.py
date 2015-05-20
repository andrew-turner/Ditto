class Animation():
   """
   Class to provide tile animation

   Animation(frames)

   play(loop, start=0)
   tick()

   active
   currentFrame
   """
   
   def __init__(self, frames):
      """
      Setup the animation, not playing yet.

      frames - list of tile indexes to iterate through when played.
      """

      #store the frame list
      self._frames = frames
      self._length = len(self._frames)

      #set variables
      self._loop = False
      self._current = 0
      self._active = False

   def play(self, loop, start=0):
      """
      Start the animation playing.

      loop - whether or not to loop the animation at the end.
      start - the frame to start at.
      """

      #set the animation up and set it active
      self._loop = loop
      self._current = start
      self._active = True

   @property
   def active(self):
      return self._active

   @property
   def currentFrame(self):
      """Gets the current frame of the animation."""

      #return the required frame
      return self._frames[self._current]

   def tick(self):
      """Advance the animation."""

      #advance the animation, then check whether we've reached the end
      #if so, go back to the start, and if we're not looping set inactive
      self._current += 1
      if self._current >= self._length:
         self._current = 0
         if not self._loop:
            self._active = False
