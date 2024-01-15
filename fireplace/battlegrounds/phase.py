from enum import IntEnum


class Phase(IntEnum):
    INVALID = 0
    CHOOSE_HERO = 1
    RECRUIT = 2
    COMBAT = 3
