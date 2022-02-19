"""
Contains the abstract YamlConfig base class
"""

from abc import ABC
from typing import Optional


class YamlConfig(ABC):
    """
    The base structure for all configuration files
    """

    def __init__(self, metadata: Optional[dict], spec: dict) -> None:
        self.metadata = metadata
        self.spec = spec

    def __getitem__(self, key: str) -> dict:
        return self.spec[key]
