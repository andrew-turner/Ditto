from pygame.locals import *

from eng.constants.buttons import *

DEBUG = False
ACCELERATE_DEBUG = False

screenSize = 19,15

framerate = 22
textSpeed = "MEDIUM"

music = True
soundEffects = True

path = ".\\ExampleGame"

keys = {K_UP: BT_UP,
        K_DOWN: BT_DOWN,
        K_LEFT: BT_LEFT,
        K_RIGHT: BT_RIGHT,
        K_z: BT_A,
        K_x: BT_B,
        K_RETURN: BT_START,
        K_BACKSPACE: BT_SELECT,
        K_s: BT_SAVE,
        K_q: BT_DEBUG,
        K_SPACE: BT_TURBO}
