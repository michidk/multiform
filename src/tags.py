"""
Customizes the PyYAML loading and dumping
"""

import yaml


class RefTag(yaml.YAMLObject):
    """
    Custom tag for referencing other components in architecture definitions
    """

    __yaml_tag = "!ref"

    def __init__(self, value: str):
        self.value = value

    def __repr__(self):
        return self.value  # transiently return our value

    @classmethod
    def from_yaml(cls, loader: yaml.Loader, node: dict):
        return RefTag(node.value)

    @classmethod
    def to_yaml(cls, dumper: yaml.Dumper, data: dict):
        return dumper.represent_scalar(cls.__yaml_tag, data.value)


def architecture_loader():
    """Add constructors to PyYAML loader"""
    loader = yaml.SafeLoader
    loader.add_constructor("!ref", RefTag.from_yaml)
    return loader


def architecture_dumper():
    """Add representers to PyYAML dumper"""
    dumper = yaml.SafeDumper
    dumper.add_multi_representer(RefTag, RefTag.to_yaml)
    return dumper


def report_dumper():
    """Custom PyYAML dumper for reports"""
    dumper = yaml.SafeDumper
    dumper.ignore_aliases = lambda *args: True  # disable aliases
    return dumper
