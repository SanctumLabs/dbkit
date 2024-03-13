"""
Contains a square that represents a "square" on the maze
"""
from dataclasses import dataclass

from .border import Border
from .role import Role


@dataclass(frozen=True)
class Square:
    """
    Represents a square in the maze
    Args:
        index (int): Keeps track of this square's 1 dimensional index within a flat sequence of squares
        row (int): Keeps track of the row number
        column (int): Keeps track of the column number
        border (Border): The type of border for this square
        role (Role): The role of this square, Defaults to None.
    """

    index: int
    row: int
    column: int
    border: Border
    role: Role = Role.NONE
