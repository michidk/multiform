"""
Contains the architecture class
"""

from __future__ import annotations

from collections import Counter
from typing import Optional, Tuple, Union

from . import utils
from .config import YamlConfig
from .tags import RefTag


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

    def check_naming_collisions(self) -> list[str]:
        """
        Checks for naming collisions: ensure every component name is unique
        """
        names: list[str] = map(lambda x: x["name"], self.components())
        counter = Counter(names)
        return [i for i, j in counter.items() if j > 1]

    def check_references(self) -> list[Tuple[str, str, str]]:
        """
        Validates all component references: ensure every reference points to a valid component
        """
        cnames: list[str] = list(map(lambda x: x["name"], self.components()))

        invalid_refs: list[Tuple[str, str, str]] = []
        for component in self.components():
            if "properties" in component:
                properties: dict[str, Union[str, dict, RefTag]] = component[
                    "properties"
                ]
                for name, tag in utils.get_type_occurences(properties, RefTag):
                    if not tag.value in cnames:
                        invalid_refs.append((component["name"], name, tag.value))

        return invalid_refs

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
