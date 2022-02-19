"""
Custom Cerberus validator
"""

from cerberus import TypeDefinition, Validator

from .tags import RefTag


class CustomValidator(Validator):
    """
    Defines the custom validator
    """

    __ref_type = TypeDefinition("reference", (RefTag,), ())
    types_mapping = Validator.types_mapping.copy()
    types_mapping["reference"] = __ref_type
