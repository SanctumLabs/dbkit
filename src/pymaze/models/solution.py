"""
Model of the solution to a maze
"""
from dataclasses import dataclass
from typing import Tuple, Iterator
from functools import reduce

from .square import Square
from .role import Role


@dataclass(frozen=True)
class Solution:
    """
    Sequence of square objects that originate from the maze entrance to the exit.
    Note, however, that this may jump over a few squares at a time without stepping on each as long as they line up
    horizontally or vertically. This reflects how to represent the path through the maze as an ordered collection of
    nodes in a graph.

    This is similar to the Maze object, however, this is one-dimensional instead of representing rows and columns.
    """

    squares: Tuple[Square, ...]

    def __post_init__(self) -> None:
        """This will validate the solution to ensure that this provides the actual solution to a maze and not a random
        sequence of squares in the maze"""
        assert self.squares[0].role is Role.ENTRANCE
        assert self.squares[-1].role is Role.EXIT
        reduce(validate_corridor, self.squares)

    def __iter__(self) -> Iterator[Square]:
        """makes the solution class iterable, allowing iteration through the squares"""
        return iter(self.squares)

    def __getitem__(self, index: int) -> Square:
        """adds a subscriptable property to the class allowing retrieving a square given an index"""
        return self.squares[index]

    def __len__(self) -> int:
        """adds retrieving the length of the solution, i.e. number of squares"""
        return len(self.squares)


def validate_corridor(current: Square, following: Square) -> Square:
    """
    Validates a corridor by getting the current square's row or column and comparing it to the next square's row or
    column. These must match for it to be a valid corridor.
    This returns the following/next square to compare against the following's next square.

    Args:
        current (Square): Current square to check against next square
        following (Square): Following or next square

    Return:
        Square: The next square
    """
    assert any(
        [current.row == following.row, current.column == following.column]
    ), "Squares must lie on the same row or column"
    return following
