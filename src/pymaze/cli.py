"""
Defines the CLI command arguments
"""
import sys
import argparse
from argparse import Namespace
from pathlib import Path


def get_command_line_args() -> Namespace:
    """
    Creates a parser and adds arguments for the parser returning the namespace for the argument parser to use in a CLI
    Returns:
        Namespace: populated namespace object
    """
    parser = argparse.ArgumentParser(
        prog="pymaze",
        description="Solve mazes directly from the CLI",
        epilog="Thank you for using PyMaze CLI",
    )

    # Argument to get the version name
    parser.add_argument(
        "-v",
        "--version",
        action="version",
    )

    # Argument to get the directory name
    parser.add_argument(
        "path",
        type=Path,
        default=".",
        help="Generate full directory tree starting at ROOT_DIR",
    )

    return parser.parse_args()
