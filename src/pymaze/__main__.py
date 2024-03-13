"""
Entry point of the maze solver
"""
from .cli import get_command_line_args
from .models import Maze
from .graphs.solver import solve_all
from .view.renderer import SVGRenderer


def main() -> None:
    """Entry point of the maze solver application"""
    args = get_command_line_args()
    maze = Maze.load(args.path)
    solutions = solve_all(maze)
    if solutions:
        renderer = SVGRenderer()
        for solution in solutions:
            svg = renderer.render(maze, solution)
            svg.preview()


if __name__ == "__main__":
    main()
