"""
Contains roles for squares in the grid
"""
from enum import IntEnum, auto


class Role(IntEnum):
    """
    Represents the role of each square in the maze
    """

    NONE = 0
    ENEMY = auto()
    ENTRANCE = auto()
    EXIT = auto()
    EXTERIOR = auto()
    REWARD = auto()
    WALL = auto()
