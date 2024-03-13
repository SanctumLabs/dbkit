"""
Contains the maze model
"""
from typing import Tuple, Iterator
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

from .square import Square
from .role import Role
from ..persistence.serializer import dump_squares, load_squares


@dataclass(frozen=True)
class Maze:
    """
    Represents the maze
    """

    squares: Tuple[Square, ...]

    def __post_init__(self) -> None:
        """Validates the maze on initialization"""
        validate_indices(self)
        validate_rows_columns(self)
        validate_entrance(self)
        validate_exit(self)

    def __iter__(self) -> Iterator[Square]:
        """
        Makes the class iterable and returns an iterator of squares
        Return:
            Iterator: iterator of squares
        """
        return iter(self.squares)

    def __getitem__(self, index: int) -> Square:
        """
        Makes the maze subscriptable, allowing access of a square given an index
        """
        return self.squares[index]

    @cached_property
    def width(self) -> int:
        """
        Cached property allowing access to the width of the maze.
        This is determined by getting the maximum of the column of the squares in the maze & adding 1 to it to account
        for zero-based indexing.
        """
        return max(square.column for square in self) + 1

    @cached_property
    def height(self) -> int:
        """
        Cached property allowing access to the height of the maze.
        This is determined by getting the maximum row of the squares in the maze & adding 1 to it to account
        for zero-based indexing.
        """
        return max(square.row for square in self) + 1

    @cached_property
    def entrance(self) -> Square:
        """
        Cached property that returns the entrance of the maze
        """
        return next(square for square in self if square.role is Role.ENTRANCE)

    @cached_property
    def exit(self) -> Square:
        """
        Cached property that returns the exit of the maze
        """
        return next(square for square in self if square.role is Role.EXIT)

    @classmethod
    def load(cls, path: Path) -> "Maze":
        """Factory function to create a maze from a path to a file"""
        return cls(squares=tuple(load_squares(path)))

    def dump(self, path: Path) -> None:
        """Dumps the maze onto the provided path"""
        dump_squares(self.width, self.height, self.squares, path)


def validate_indices(maze: Maze) -> None:
    """
    Validates the indices of the squares in the maze
    Args:
        maze (Maze): Maze to validate
    """
    assert [square.index for square in maze] == list(
        range(len(maze.squares))
    ), "Wrong square.index"


def validate_rows_columns(maze: Maze) -> None:
    """
    Validates the rows and columns of the squares in the maze
    Args:
        maze (Maze): Maze to validate
    """
    for h in range(maze.height):
        for w in range(maze.width):
            square = maze[h * maze.width + w]
            assert square.row == h, "Wrong square.row"
            assert square.column == w, "Wrong square.column"


def validate_entrance(maze: Maze) -> None:
    """Validates that a maze has an entrance"""
    assert 1 == sum(
        1 for square in maze if square.role is Role.ENTRANCE
    ), "Must have exactly 1 entrance"


def validate_exit(maze: Maze) -> None:
    """Validates that a maze has exactly one exit"""
    assert 1 == sum(
        1 for square in maze if square.role is Role.EXIT
    ), "Must have exactly 1 exit"
