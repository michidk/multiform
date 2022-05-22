"""
Contains common functionality, required by multiple subcommands
"""

from typing import Tuple

import jinja2
from loguru import logger

from .architecture import ArchitectureConfig
from .schema import Schema, SchemaRegistry


def init(
    architecture: str,
) -> Tuple[jinja2.Environment, SchemaRegistry, ArchitectureConfig]:
    """
    Initialization routine for the transpiler and graph subcommands
    """
    logger.info("Initializing...")

    # setup templating engine
    env = jinja2.Environment(
        loader=jinja2.BaseLoader(),
    )

    # read & validate schemas
    logger.info("Reading and validation schemas...")
    schema_registry: SchemaRegistry = Schema.load_all()

    # load architecture definition
    logger.info("Loading user-provided architecture definition file...")

    # TODO: verify unique component names
    architecture: ArchitectureConfig = ArchitectureConfig.with_schema_registry(
        architecture, schema_registry
    )

    return env, schema_registry, architecture
