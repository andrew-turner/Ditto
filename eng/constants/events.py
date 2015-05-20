#define constants
EV_INVESTIGATE = 0
EV_WALKONTO = 1
EV_FINISHWALKONTO = 2
EV_LOAD = 3
EV_NEWGAME = 4

TRIGGERNAMES = {"investigate": EV_INVESTIGATE,
                "walkonto": EV_WALKONTO,
                "finishwalkonto": EV_FINISHWALKONTO,
                "load": EV_LOAD,
                "newgame": EV_NEWGAME}

#import
__all__ = ("EV_INVESTIGATE",
           "EV_WALKONTO",
           "EV_FINISHWALKONTO",
           "EV_LOAD",
           "EV_NEWGAME",
           "TRIGGERNAMES")
