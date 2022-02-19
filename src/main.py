"""
Contains the main entrypoint for this application
"""

import argparse
import sys

from loguru import logger

from .graph import plot
from .transpiler import transpile


def main() -> None:
    """
    Entrypoint of the application
    """
    args = parse_args()

    setup_logging(args.verbosity)

    if args.command == "transpile":
        # todo: verify valid dirs
        transpile(
            args.architecture, args.templates, args.output, args.report, args.debug
        )
    elif args.command == "plot":
        plot(args.architecture, args.output, args.format)


def parse_args() -> dict:
    """
    Setup the CLI interface
    """

    parser = argparse.ArgumentParser(
        description="Templating engine for cloud architectures"
    )
    parser.add_argument(
        "--verbosity",
        "-v",
        default="info",
        dest="verbosity",
        nargs="?",
        choices=["trace", "debug", "info", "success", "warning", "error", "critical"],
        help="set the logging level",
    )

    subparsers = parser.add_subparsers(
        help="sub commands", required=True, dest="command"
    )
    transpile_parser = subparsers.add_parser(
        "transpile", help="transpiles the given architecture"
    )
    transpile_parser.add_argument(
        "--architecture",
        "-a",
        default="architecture.yaml",
        dest="architecture",
        required=True,
        help="the architecture definition file",
    )
    transpile_parser.add_argument(
        "--output", "-o", default="out/", dest="output", help="the output directory"
    )
    transpile_parser.add_argument(
        "--templates",
        "-t",
        default="templates/",
        dest="templates",
        help="the template directory",
    )
    transpile_parser.add_argument(
        "--report",
        "-r",
        action="store_true",
        dest="report",
        help="generates a report of the generated files",
    )
    transpile_parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        dest="debug",
        help="enable debug output and report",
    )

    plot_parser = subparsers.add_parser(
        "plot", help="generates a graphviz .dot file of the architecture"
    )
    plot_parser.add_argument(
        "--architecture",
        "-a",
        default="architecture.yaml",
        dest="architecture",
        required=True,
        help="the architecture definition file",
    )
    plot_parser.add_argument(
        "--output", "-o", default="out.dot", dest="output", help="the generated file"
    )
    plot_parser.add_argument(
        "--format",
        "-f",
        default="dot",
        dest="format",
        nargs="?",
        choices=[
            "neato",
            "dot",
            "twopi",
            "circo",
            "fdp",
            "nop",
            "osage",
            "patchwork",
            "gc",
            "acyclic",
            "gvpr",
            "gvcolor",
            "ccomps",
            "sccmap",
            "tred",
            "sfdp",
            "unflatten",
        ],
        help="the file format of the output",
    )

    return parser.parse_args()


def setup_logging(verbosity: str) -> None:
    """
    Sets up the logging system
    """
    logger.remove()
    logger.add(sys.stderr, level=verbosity.upper(), backtrace=True, colorize=True)


if __name__ == "__main__":
    main()
