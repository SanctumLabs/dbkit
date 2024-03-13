"""
Handles SVG rendering
"""
import textwrap
from dataclasses import dataclass
import webbrowser
import tempfile
from ..models.maze import Maze
from ..models.role import Role
from ..models.solution import Solution
from ..models.square import Square
from ..view.primitives import tag, Rect, Point, Text, Polyline
from ..view.decomposer import decompose

ROLE_EMOJI = {
    Role.ENTRANCE: "\N{pedestrian}",
    Role.EXIT: "\N{chequered flag}",
    Role.ENEMY: "\N{ghost}",
    Role.REWARD: "\N{white medium star}",
}


def arrow_marker() -> str:
    """
    Renders an arror marker indicating an exit from the maze
    """
    return tag(
        "defs",
        tag(
            "marker",
            tag("path", d="M 0,0 L 10,5 L 0,10 2,5 z", fill="red", fill_opacity="50%"),
            id="arrow",
            viewBox="0 0 20 20",
            refX="2",
            refY="5",
            markerUnits="strokeWidth",
            markerWidth="10",
            markerHeight="10",
            orient="auto",
        ),
    )


def background() -> str:
    """Draws a background"""
    return Rect().draw(width="100%", height="100%", fill="white")


@dataclass(frozen=True)
class SVG:
    """
    SVG element
    """

    xml_content: str

    @property
    def html_content(self) -> str:
        """HTML content of the svg content"""
        return textwrap.dedent(
            """\
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <title>SVG Preview</title>
        </head>
        <body>
        {0}
        </body>
        </html>"""
        ).format(self.xml_content)

    def preview(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".html", delete=False
        ) as file:
            file.write(self.html_content)
        webbrowser.open(f"file://{file.name}")


@dataclass(frozen=True)
class SVGRenderer:
    """
    A scalable vector graphics renderer will take the square size and line width in pixel coordinates as input
    parameters assuming sensible defaults
    """

    square_size: int = 100
    line_width: int = 6

    @property
    def offset(self) -> int:
        """
        The offset is the distance from the top and left edge of the drawing space, which takes your line width into
        account. Without it, a line starting in the top-left corner would be drawn at the very edge of the canvas and
        partially out of view.
        """
        return self.line_width // 2

    def render(self, maze: Maze, solution: Solution | None = None) -> SVG:
        """
        Renders a lightweight SVG object which wraps the textual XML content
        """
        margins = 2 * (self.offset + self.line_width)
        width = margins + maze.width * self.square_size
        height = margins + maze.height * self.square_size

        return SVG(
            tag(
                "svg",
                self._get_body(maze, solution),
                xmlns="http://www.w3.org/2000/svg",
                stroke_linejoin="round",
                width=width,
                height=height,
                viewBox=f"0 0 {width} {height}",
            )
        )

    def _get_body(self, maze: Maze, solution: Solution | None) -> str:
        """Retrieves the body from the maze and solution"""
        return "".join(
            [
                arrow_marker(),
                background(),
                *map(self._draw_square, maze),
                self._draw_solution(solution) if solution else "",
            ]
        )

    def _transform(self, square: Square, extra_offset: int = 0) -> Point:
        """Scales and transforms the square's coordinates using the desired square size and offset"""
        return Point(
            x=square.column * self.square_size,
            y=square.row * self.square_size,
        ).translate(x=self.offset + extra_offset, y=self.offset + extra_offset)

    def _draw_square(self, square: Square) -> str:
        """Draws a square"""
        top_left: Point = self._transform(square)
        tags = [self._draw_border(square, top_left)]
        if square.role is Role.EXTERIOR:
            tags.append(exterior(top_left, self.square_size, self.line_width))
        elif square.role is Role.WALL:
            tags.append(wall(top_left, self.square_size, self.line_width))
        elif emoji := ROLE_EMOJI.get(square.role):
            tags.append(label(emoji, top_left, self.square_size // 2))
        return "".join(tags)

    def _draw_border(self, square: Square, top_left: Point) -> str:
        """Draws the border"""
        return decompose(square.border, top_left, self.square_size).draw(
            stroke_width=self.line_width, stroke="black", fill="none"
        )

    def _draw_solution(self, solution: Solution) -> str:
        """Draws the solution"""
        return Polyline(
            [self._transform(point, self.square_size // 2) for point in solution]
        ).draw(
            stroke_width=self.line_width * 2,
            stroke_opacity="50%",
            stroke="red",
            fill="none",
            marker_end="url(#arrow)",
        )


def exterior(top_left: Point, size: int, line_width: int) -> str:
    """Renders the exterior"""
    return Rect(top_left).draw(
        width=size, height=size, stroke_width=line_width, stroke="none", fill="white"
    )


def wall(top_left: Point, size: int, line_width: int) -> str:
    """Renders a wall"""
    return Rect(top_left).draw(
        width=size,
        height=size,
        stroke_width=line_width,
        stroke="none",
        fill="lightgray",
    )


def label(emoji: str, top_left: Point, offset: int) -> str:
    """Renders a label"""
    return Text(emoji, top_left.translate(x=offset, y=offset)).draw(
        font_size=f"{offset}px", text_anchor="middle", dominant_baseline="middle"
    )
