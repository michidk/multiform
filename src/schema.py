"""
Contains the Schema class
"""

from __future__ import annotations

import os
from typing import Callable, NewType

from loguru import logger

from . import utils
from .config import YamlConfig

SchemaRegistry = NewType("SchemaRegistry", dict[str, "Schema"])


class Schema(YamlConfig):
    """
    Represents a schema in memory
    """

    DEFAULT_SCHEMA_PATH: str = "src/schemas"

    def __init__(self, metadata: dict, spec: dict) -> None:
        super().__init__(metadata, spec)
        self.name = metadata["name"]

    def validate(self, data: dict) -> dict:
        """
        Validates the data against the schema
        """
        utils.load_yaml_and_validate_handle_errors(data, self.spec)

    @staticmethod
    def __kind_check_fn(kind: str) -> Callable[[str, str, dict], dict]:
        """
        Returns a utility function that checks if a schema is of the given kind
        """

        def is_kind(field, value, error):
            if not value == kind:
                error(field, f"must be '{kind}'")

        return is_kind

    @staticmethod
    def __master_schema() -> dict:
        """
        Returns the master schema that all schemas must adhere to
        """
        return {
            "kind": {
                "type": "string",
                "required": False,
                "check_with": Schema.__kind_check_fn("Schema"),
            },
            "metadata": {
                "type": "dict",
                "required": True,
                "schema": {
                    "name": {
                        "type": "string",
                        "required": True,
                    },
                },
            },
            "spec": {
                "type": "dict",
                "required": True,
            },
        }

    @staticmethod
    def load(path: str) -> Schema:
        """
        Loads a schema file from path and returns the data as a dict.
        """
        schema = utils.load_yaml(path)

        # validate against master schema
        success, errors = utils.validate(schema, Schema.__master_schema())
        if not success:
            logger.error(f"Wrong yaml format for {path}: {errors}")
            exit(1)

        # add kind verification to spec
        schema["spec"]["kind"] = {
            "type": "string",
            "required": False,
            "check_with": Schema.__kind_check_fn(schema["metadata"]["name"]),
        }

        return Schema(schema["metadata"], schema["spec"])

    @staticmethod
    def load_all(path: str = DEFAULT_SCHEMA_PATH) -> SchemaRegistry:
        """
        Loads all schemas from `path`
        """
        schemes: SchemaRegistry = {}

        for file in os.listdir(path):
            file_path = os.path.join(path, file)

            # ignore folders etc
            if not os.path.isfile(file_path):
                continue

            schema = Schema.load(file_path)
            schemes[schema.name] = schema

        return schemes
