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

    return env, schema_registry, load_architecture(architecture, schema_registry)


def load_architecture(
    architecture: str, schema_registry: SchemaRegistry
) -> ArchitectureConfig:
    """
    Loads and validates the architecture
    """
    logger.info("Loading user-provided architecture definition file...")

    # load architecture definition
    architecture: ArchitectureConfig = ArchitectureConfig.with_schema_registry(
        architecture, schema_registry
    )

    logger.info("Validating architecture")

    # check for naming collisions
    collisions: list[str] = architecture.check_naming_collisions()
    if len(collisions) >= 1:
        logger.error(
            f"Found architecture component name collisions (names have to be unique): {collisions}"
        )
        exit(1)

    return architecture
