"""
Utility functions
"""

import os
import sys
from typing import Tuple

import cerberus
import yaml
from loguru import logger


def load_text(path: str) -> str:
    """
    Loads a text file from path and returns the string.
    """
    try:
        with open(path, "r", encoding="utf8") as stream:
            return stream.read()
    except FileNotFoundError:
        logger.exception(f"'{path}' not found")
        sys.exit(1)


def load_yaml(path: str, loader: yaml.Loader = yaml.SafeLoader) -> dict:
    """
    Loads a yaml file from path and returns the data as a dict.
    """
    try:
        with open(path, "r", encoding="utf8") as stream:
            return yaml.load(stream, Loader=loader)
    except FileNotFoundError:
        logger.exception(f"'{path}' not found")
        sys.exit(1)
    except yaml.YAMLError:
        logger.exception(f"Error parsing '{path}'")
        sys.exit(1)


def validate(
    data: dict, schema: dict, validator: cerberus.Validator = cerberus.Validator()
) -> tuple[bool, dict]:
    """
    Validates data against a schema.
    """
    try:
        success = validator.validate(data, schema)
    except cerberus.schema.SchemaError:
        logger.exception("Error parsing schema")
        sys.exit(1)

    return (success, validator.errors)


def load_yaml_and_validate(
    path: str,
    schema: dict,
    loader: yaml.Loader = yaml.SafeLoader,
    validator: cerberus.Validator = cerberus.Validator(),
) -> tuple[bool, dict, dict]:
    """
    Loads a yaml file from path and validates it against a schema.
    """
    data = load_yaml(path, loader)
    success, errors = validate(data, schema, validator)
    return (success, errors, data)


def load_yaml_and_validate_handle_errors(
    path: str,
    schema: dict,
    loader: yaml.Loader = yaml.SafeLoader,
    validator: cerberus.Validator = cerberus.Validator(),
) -> dict:
    """
    Loads a yaml file from path and validates it against a schema while handling the errors.
    """
    success, errors, data = load_yaml_and_validate(path, schema, loader, validator)
    if not success:
        logger.error(f"Error parsing '{path}': {errors}")
        sys.exit(1)

    return data


def default_file_from_path(path: str, default_file: str) -> str:
    """
    Returns the default file from a path if the path does not already specify a file.
    """

    if os.path.isdir(path):
        path = os.path.join(path, default_file)

    if not os.path.isfile(path):
        logger.error(f"Template file {path} does not exist")
        exit(1)

    return path


def default_extension_from_path(path: str, default_ext: str) -> str:
    """
    Returns the file with the default extension from a path if the path does not already specify an extension.
    """

    if not os.path.isfile(path):
        path = f"{path}{default_ext}"

    if not os.path.isfile(path):
        logger.error(f"Template file {path} does not exist")
        exit(1)

    return path


def get_type_occurences(dictionary: dict, search_type: type) -> list[Tuple[str, type]]:
    """
    Recursively finds all instances of a given type in a dictionary
    """
    ref_tags: list[Tuple[str, type]] = []

    for name, value in dictionary.items():
        if isinstance(value, dict):
            ref_tags.extend(get_type_occurences(value, search_type))
        if isinstance(value, search_type):
            ref_tags.append((name, value))

    return ref_tags
