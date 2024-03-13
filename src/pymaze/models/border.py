"""
Border represents the border of a square
"""
from enum import IntFlag, auto


class Border(IntFlag):
    """
    Contains the direction of the border on a given square. This will allow combining the members to create a composite
    value.
    """

    EMPTY = 0
    TOP = auto()
    BOTTOM = auto()
    LEFT = auto()
    RIGHT = auto()

    @property
    def corner(self) -> bool:
        """
        Uses the membership test operator (in), to check if an instance of the Border enumeration—indicated by self—is
        one of the predefined corners.
        Returns:
            bool: True if this is a corner, False otherwise
        """
        return self in (  # type: ignore[comparison-overlap]
            self.TOP | self.LEFT,
            self.TOP | self.RIGHT,
            self.BOTTOM | self.LEFT,
            self.BOTTOM | self.RIGHT,
        )

    @property
    def dead_end(self) -> bool:
        """
        Property to check if a border is a dead end relying on the bit_count() method which returns the number of ones
        in the binary representation of a border.
        Returns:
            bool: True if this is a dead end, False otherwise
        """
        return self.bit_count() == 3

    @property
    def intersection(self) -> bool:
        """
        Property to check if a border is an intersection relying on the bit_count() method which returns the number of
        ones in the binary representation of a border.
        Returns:
            bool: True if this is an intersection, False otherwise

        """
        return self.bit_count() < 2
