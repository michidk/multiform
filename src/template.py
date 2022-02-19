"""
Contains the template classes
"""

from __future__ import annotations

import os
from typing import Optional, Type

import jinja2
from loguru import logger

from . import utils
from .config import YamlConfig
from .schema import Schema


class TemplateConfig(YamlConfig):
    """
    A base class representing a config file from the /templates folder that is based on a `Schema`
    """

    def __init__(self, schema: Schema, metadata: Optional[dict], spec: dict) -> None:
        super().__init__(metadata, spec)
        self.schema = schema

    @staticmethod
    def load(path: str, schema: Schema, base_type: Type, **kwargs: any) -> type:
        """
        Creates a TemplateRoot from a path and a schema
        """
        data: dict = utils.load_yaml_and_validate_handle_errors(path, schema.spec)

        return base_type(schema, data.get("metadata"), data["spec"], **kwargs)


class TemplateRoot(TemplateConfig):
    """
    Represents the template root file that exists once per templates/ folder
    """

    SCHEMA_NAME: str = "TemplateRoot"

    def __init__(self, schema: Schema, metadata: Optional[dict], spec: dict) -> None:
        super().__init__(schema, metadata, spec)

    @staticmethod
    def with_schema_registry(
        path: str, schema_registry: dict[str, dict]
    ) -> TemplateRoot:
        """
        Creates a TemplateRoot from a path
        """
        return TemplateRoot.load(
            path, schema_registry[TemplateRoot.SCHEMA_NAME], TemplateRoot
        )


class TemplateDefinition(TemplateConfig):
    """
    A template is a collection of resources that can be deployed to multiple cloud providers
    """

    SCHEMA_NAME: str = "TemplateDefinition"

    def __init__(
        self,
        schema: Schema,
        metadata: Optional[dict],
        spec: dict,
        template_type: str,
        template_files: dict[str, list[TemplateFile]],
    ) -> None:
        super().__init__(schema, metadata, spec)
        self.template_type = template_type
        self.template_files = template_files

    def validate_properties(self, data: dict) -> bool:
        """
        Validates the properties of the template
        """
        if "properties" not in self.spec or self.spec["properties"] is None:
            if len(data.items()) > 0:
                logger.error(
                    f"Template `{self.template_type}` has no properties defined, but provided component data has properties"
                )
                return False
            else:
                return True
        success, errors = utils.validate(data, self.spec["properties"])

        # TODO: validate references

        if not success:
            logger.error(
                f"Wrong properties for template `{self.template_type}`: {errors}"
            )
            return False
        else:
            return True

    def render(
        self, platform: str, env: jinja2.Environment, data: dict
    ) -> Optional[list[RenderedFile]]:
        """
        Renders the template files for a given platform
        """
        if not platform in self.template_files:
            logger.error(
                f"No definition of template `{self.template_type}` found for platform `{platform}`."
            )
            exit(1)

        return list(map(lambda x: x.render(env, data), self.template_files[platform]))

    @staticmethod
    def parse_template(
        template_dir: str, template_type: str, platform: str, file: str
    ) -> TemplateFile:
        """
        Parses a single template file
        """
        return TemplateFile.parse(
            os.path.join(template_dir, template_type, file),
            template_type,
            platform,
        )

    @staticmethod
    def from_schemas(
        template_dir: str, template_type: str, path: str, schemas: dict[str, dict]
    ) -> TemplateDefinition:
        """
        Parses all files that belong to this template
        """
        schema: dict = schemas[TemplateDefinition.SCHEMA_NAME]
        data: dict = utils.load_yaml_and_validate_handle_errors(path, schema.spec)
        template_files: dict[str, list[TemplateFile]] = {}

        for platform in data["spec"]["platforms"]:

            if isinstance(platform, str):
                template_files[platform] = [
                    TemplateDefinition.parse_template(
                        template_dir, template_type, platform, platform
                    )
                ]

            elif isinstance(platform, dict):
                for platform_name, file_list in platform.items():
                    template_files[platform_name] = []
                    for file in file_list:
                        template_files[platform_name].append(
                            TemplateDefinition.parse_template(
                                template_dir, template_type, platform_name, file
                            )
                        )

            else:
                logger.error(f"{template_type}: Invalid platform type")
                exit(1)

        return TemplateDefinition(
            schema, data.get("metadata"), data["spec"], template_type, template_files
        )


class TemplateFile:
    """
    A template file is a single file that can be deployed to multiple cloud providers
    """

    def __init__(
        self, path: str, template_type: str, platform: str, contents: str
    ) -> None:
        self.path = path
        self.template_type = template_type
        self.platform = platform
        self.contents = contents

    def render(self, env: jinja2.Environment, data: dict) -> RenderedFile:
        """
        Renders the template
        """
        try:
            rendered_text = env.from_string(self.contents).render(data)
        except jinja2.exceptions.TemplateError as err:
            logger.error(f"{self.path}: {err}")
            exit(1)
        return RenderedFile(self, rendered_text)

    @staticmethod
    def parse(path: str, template_type: str, platform: str) -> TemplateFile:
        """
        Parses a file
        """
        path: str = utils.default_extension_from_path(path, ".tf.j2")
        logger.debug(f"File: {template_type} - {platform} -> {path}")

        text_contents = utils.load_text(path)

        return TemplateFile(path, template_type, platform, text_contents)


class RenderedFile:
    """
    A rendered file is a single file that has been rendered to a string
    """

    def __init__(self, template: TemplateFile, contents: str) -> None:
        self.template = template
        self.contents = contents

    def save(self, out_dir: str, name: str) -> str:
        """
        Writes the file to disk, returning the path to the file
        """
        suffix = (
            os.path.basename(self.template.path)
            .removesuffix(".tf.j2")
            .replace(self.template.platform, "")
        )

        target_path: str = os.path.join(out_dir, f"{name}{suffix}.tf")

        with open(target_path, "w", encoding="utf8") as file:
            file.write(self.contents)

        return target_path
