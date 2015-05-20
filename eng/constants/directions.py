#define direction constants
DIR_UP = 0
DIR_DOWN = 1
DIR_LEFT = 2
DIR_RIGHT = 3

#for scripting movements
STEPNAMES = {"u": DIR_UP,
             "d": DIR_DOWN,
             "l": DIR_LEFT,
             "r": DIR_RIGHT}

#import
__all__ = ("DIR_UP",
           "DIR_DOWN",
           "DIR_LEFT",
           "DIR_RIGHT",
           "STEPNAMES")
