"""
Decompose module used to decompose primitives
"""
from ..models.border import Border
from ..view.primitives import (
    Line,
    Point,
    Primitive,
    Polygon,
    Polyline,
    DisjointLines,
    NullPrimitive,
)


def decompose(border: Border, top_left: Point, square_size: int) -> Primitive:
    """
    This takes a border pattern, the top-left corner of the corresponding square in SVG coordinates, and the desired
    square size in SVG coordinates as input. Its goal is to decompose the border into a relevant geometric primitive
    that can be drawn.

    First, it locates the other corners of the current square’s border by translating the point that was provided as a
    function parameter. Next, it creates the four sides of the border by connecting the corners into lines accordingly.
    Once it has all the sides and corners, it constructs the polygon, polyline, or lines associated with the given
    border pattern.

    Args:
        border (Border): border pattern
        top_left (Point): corner of the corresponding square in SVG coordinates
        square_size (int): desired square size in SVG coordinates.

    Returns:
        Primitive: SVG Primitive
    """
    top_right: Point = top_left.translate(x=square_size)
    bottom_right: Point = top_left.translate(x=square_size, y=square_size)
    bottom_left: Point = top_left.translate(y=square_size)

    top = Line(top_left, top_right)
    bottom = Line(bottom_left, bottom_right)
    left = Line(top_left, bottom_left)
    right = Line(top_right, bottom_right)

    if border is Border.LEFT | Border.TOP | Border.RIGHT | Border.BOTTOM:
        return Polygon([top_left, top_right, bottom_left, bottom_right])

    if border is Border.BOTTOM | Border.LEFT | Border.TOP:
        return Polyline(
            [
                bottom_right,
                bottom_left,
                top_left,
                top_right,
            ]
        )

    if border is Border.LEFT | Border.TOP | Border.RIGHT:
        return Polyline(
            [
                bottom_left,
                top_left,
                top_right,
                bottom_right,
            ]
        )

    if border is Border.TOP | Border.RIGHT | Border.BOTTOM:
        return Polyline(
            [
                top_left,
                top_right,
                bottom_right,
                bottom_left,
            ]
        )

    if border is Border.RIGHT | Border.BOTTOM | Border.LEFT:
        return Polyline(
            [
                top_right,
                bottom_right,
                bottom_left,
                top_left,
            ]
        )

    if border is Border.LEFT | Border.TOP:
        return Polyline(
            [
                bottom_left,
                top_left,
                top_right,
            ]
        )

    if border is Border.TOP | Border.RIGHT:
        return Polyline(
            [
                top_left,
                top_right,
                bottom_right,
            ]
        )

    if border is Border.BOTTOM | Border.LEFT:
        return Polyline(
            [
                bottom_right,
                bottom_left,
                top_left,
            ]
        )

    if border is Border.RIGHT | Border.BOTTOM:
        return Polyline(
            [
                top_right,
                bottom_right,
                bottom_left,
            ]
        )

    if border is Border.LEFT | Border.RIGHT:
        return DisjointLines([left, right])

    if border is Border.TOP | Border.BOTTOM:
        return DisjointLines([top, bottom])

    if border is Border.TOP:
        return top

    if border is Border.RIGHT:
        return right

    if border is Border.BOTTOM:
        return bottom

    if border is Border.LEFT:
        return left

    return NullPrimitive()
