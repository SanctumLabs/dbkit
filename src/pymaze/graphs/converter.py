"""
Contains a few functions that converts a maze into a graph
"""
from typing import Set

import networkx as nx

from ..models.square import Square
from ..models.maze import Maze
from ..models.role import Role
from ..models.border import Border
from .edge import Edge, Node


def get_nodes(maze: Maze) -> Set[Node]:
    """
    Retrieves a set of nodes from a given maze filtering out squares that are exteriors and ones that are walls.
    Args:
        maze (Maze): Maze to extract nodes from
    Returns:
        Set: set of nodes
    """
    nodes: Set[Node] = set()
    for square in maze:
        if square.role in (Role.EXTERIOR, Role.WALL):
            continue
        if square.role is not Role.NONE:
            nodes.add(square)
        if square.border.intersection or square.border.dead_end or square.border.corner:
            nodes.add(square)
    return nodes


def get_edges(maze: Maze, nodes: Set[Node]) -> Set[Edge]:
    """
    Retrieves a set of edges from a given maze and the nodes that were extracted from the maze.

    This looks for the immediate neighbors of each node supplied to the function. In this case, it moves east and south
     in the maze, but it could just as well follow the opposite directions, remembering to change the loop indexing and
     wall detection accordingly. It uses the bitwise AND operator (&) to check if a border around the current square has
      either the right or bottom side, indicating a wall that terminates the search in that direction.

    On the other hand, if it finds that a square located in the same row or column as the source node is also present
    in the set of nodes, and there’s no wall between them, then it creates an Edge instance and adds it to the set of
    edges.
    Args:
        maze (Maze): maze object
        nodes (set) of (Node): set of nodes extracted from maze
    Returns:
        set: set of edges connecting the squares
    """
    edges: Set[Edge] = set()

    for source_node in nodes:
        # follow the right node
        node = source_node

        for x in range(node.column + 1, maze.width):
            if node.border & Border.RIGHT:
                break
            node = maze.squares[node.row * maze.width + x]
            if node in nodes:
                edges.add(Edge(source_node, node))
                break

        # follow down
        node = source_node
        for y in range(node.row + 1, maze.height):
            if node.border & Border.BOTTOM:
                break
            node = maze.squares[y * maze.width + node.column]
            if node in nodes:
                edges.add(Edge(source_node, node))
                break

    return edges


def make_graph(maze: Maze) -> nx.DiGraph:
    """
    Creates a NetworkX Graph object given a Maze object
    """
    nodes = get_nodes(maze=maze)
    edges = get_directed_edges(maze=maze, nodes=nodes)
    return nx.DiGraph(
        (edge.node1, edge.node2, {"weight": edge.weight()}) for edge in edges
    )


def get_directed_edges(maze: Maze, nodes: Set[Node]) -> Set[Edge]:
    """Retrieves directed edges from a given maze and nodes"""
    return (edges := get_edges(maze, nodes)) | {edge.flip for edge in edges}
