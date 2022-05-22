"""
Generates a Graphviz graph of the given architecture
"""
import pygraphviz as pgv
from loguru import logger

from . import utils
from .architecture import ArchitectureConfig
from .common import init
from .tags import RefTag


def plot(input_file: str, out_file: str, out_format: str) -> None:
    """
    Generates the graph
    """

    architecture: ArchitectureConfig
    _, _, architecture = init(input_file)

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
