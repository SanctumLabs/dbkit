"""
Contains a edge entities representing a connection between nodes/vertices in a graph
"""
import math
from typing import NamedTuple, TypeAlias, Self

from ..models.role import Role
from ..models.square import Square

Node: TypeAlias = Square


class Edge(NamedTuple):
    """
    Represents a connection between two nodes in a graph. In this case, a connection between two squares in a maze.
    This will represent a two-way connection as we can traverse from one square to another and vice versa.
    """

    node1: Node
    node2: Node

    @property
    def distance(self) -> float:
        """
        Calculates the Euclidean distance(length of the line segment between them) between the nodes using math module,
        whose dist() function takes two points specified as sequences of coordinates. In this case, we provide tuples of
        the row and column indices of squares corresponding to the nodes. Note that you could define distance
        differently—for example, as the sum of absolute values of differences in the horizontal and vertical directions.
        """
        return math.dist(
            (self.node1.row, self.node1.column), (self.node2.row, self.node2.column)
        )

    def weight(self, bonus: int = 1, penalty: int = 2) -> float:
        """
        Retrieves the weight of the edge given a bonus(defaulted to 1) and a penalty(defaulted to 2).
        By default, this method subtracts one point from the baseline distance if the current edge leads to a reward.
        On the other hand, if there’s an enemy at the end of this edge, then the method adds two penalty points to
        increase the cost of that connection. Otherwise, the weight of an edge is equal to its distance
        """
        match self.node2.role:
            case Role.REWARD:
                return self.distance - bonus
            case Role.ENEMY:
                return self.distance + penalty
            case _:
                return self.distance

    @property
    def flip(self) -> Self:
        """
        Flips the edge from undirected to directed and vice versa
        """
        return Edge(self.node2, self.node1)  # type: ignore[return-value]
