"""
Contains the architecture class
"""

from __future__ import annotations

from typing import Optional

from . import utils
from .config import YamlConfig


class ArchitectureConfig(YamlConfig):
    """
    The architecture class parsed from YAML
    """

    SCHEMA_NAME: str = "Architecture"

    def __init__(self, metadata: Optional[dict], spec: dict) -> None:
        super().__init__(metadata, spec)

    def platforms(self) -> list:
        """
        Returns the list of platforms
        """
        return self.spec["platforms"]

    def components(self) -> list:
        """
        Returns the list of components
        """
        return self.spec["components"]

    @staticmethod
    def with_schema_registry(
        path: str, schema_registry: dict[str, dict]
    ) -> ArchitectureConfig:
        """
        Parses the architecture file from a path
        """
        schema: dict = schema_registry[ArchitectureConfig.SCHEMA_NAME]
        data: dict = utils.load_yaml_and_validate_handle_errors(path, schema.spec)

        return ArchitectureConfig(data.get("metadata"), data["spec"])
