"""
Generates a Graphviz graph of the given architecture
"""

from typing import Tuple

import jinja2
import pygraphviz as pgv
import yaml
from loguru import logger

from . import utils
from .architecture import ArchitectureConfig
from .schema import Schema
from .tags import RefTag

SCHEMA_DIR: str = "src/schemas"


def plot(input_file: str, out_file: str, out_format: str) -> None:
    """
    Generates the graph
    """

    logger.info("Initializing...")
    # setup templating engine
    env = jinja2.Environment(
        loader=jinja2.BaseLoader(),
    )

    # TODO: lots of core shared with transpiler: refactor into methods
    # read & validate schemas
    logger.info("Reading and validation schemas...")
    schema_registry: dict[str, Schema] = Schema.load_all(SCHEMA_DIR)

    # load architecture definition
    logger.info("Loading user-provided architecture definition file...")
    # TODO: load from args
    architecture: ArchitectureConfig = ArchitectureConfig.with_schema_registry(
        input_file, schema_registry
    )
    # TODO: verify unique component names

    logger.info("Building graph...")
    graph = pgv.AGraph(directed=True)

    for component in architecture.components():
        cname = component["name"]
        ctype = component["type"]
        graph.add_node(cname, label=f"{cname}: {ctype}", shape="box")

        if "properties" in component and isinstance(component["properties"], dict):
            cproperties = component["properties"]
            for name, tag in utils.get_type_occurences(cproperties, RefTag):
                graph.add_edge(cname, tag.value, label=name)

    logger.info("Finished graph")
    print(graph)

    logger.info("Saving output...")
    graph.draw(out_file, prog=out_format)
