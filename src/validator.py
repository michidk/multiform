"""
Custom Cerberus validators
"""

from cerberus import TypeDefinition, Validator

from .tags import RefTag


class ArchitectureValidator(Validator):
    """
    Validates architecture definitions
    """

    __ref_type = TypeDefinition("reference", (RefTag,), ())
    types_mapping = Validator.types_mapping.copy()
    types_mapping["reference"] = __ref_type


class PropertyValidator(ArchitectureValidator):
    """
    Validates component properties
    """

    def __init__(self, *args, **kwargs) -> None:
        if "components" in kwargs:
            self.components = kwargs["components"]
        super(PropertyValidator, self).__init__(*args, **kwargs)

    def _validate_ref_type(self, required_type, field, referenced_component):
        """
        Makes sure that the reference is of the correct type

        The rule's arguments are validated against this schema:
        {'type': 'string'}
        """
        if not isinstance(referenced_component, RefTag):
            return

        found: bool = False
        for component in self.components:
            if component["name"] == referenced_component.value:
                found = True
                typee = component["type"]
                if typee != required_type:
                    self._error(
                        field,
                        f"Invalid type in component {referenced_component} in field {field}: {typee}, expected {required_type}",
                    )

        if not found:
            self._error(
                field,
                f"No component {referenced_component} found",
            )
