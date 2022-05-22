"""
Transpiles templates to terraform files
"""

import os

import jinja2
import yaml
from loguru import logger

from . import utils
from .architecture import ArchitectureConfig
from .common import init
from .schema import Schema, SchemaRegistry
from .tags import get_report_dumper
from .template import TemplateDefinition, TemplateRoot

TEMPLATE_ROOT_FILE: str = "root.yaml"
TEMPLATE_DEFINITION_FILE: str = "definition.yaml"


def read_template_dir(
    template_dir: str, template_type: str, path: str, schemas: dict[str, Schema]
) -> TemplateDefinition:
    """
    Reads the `TEMPLATE_DEFINITION_FILE` from the template directory and returns a `Template`
    """
    # provide either a path to a template directory or a path to a template root file
    file = utils.default_file_from_path(
        os.path.join(template_dir, path), TEMPLATE_DEFINITION_FILE
    )

    return TemplateDefinition.from_schemas(template_dir, template_type, file, schemas)


def transpile(
    input_file: str, template_dir: str, out_dir: str, report: bool, debug: bool
) -> None:
    """
    Transpiles the files
    """
    mappings: list = []
    stats: dict = {"outputFiles": 0}

    jinja: jinja2.Environment
    schema_registry: SchemaRegistry
    architecture: ArchitectureConfig
    jinja, schema_registry, architecture = init(input_file)

    root: TemplateRoot = TemplateRoot.with_schema_registry(
        os.path.join(template_dir, TEMPLATE_ROOT_FILE), schema_registry
    )

    platforms: list[dict] = architecture.platforms()
    platform_names: list[str] = list(map(lambda x: x["name"], platforms))
    template_data: dict = {
        **architecture.metadata,
    }

    # create & clear output directories
    logger.info("Perparing output directories...")
    for platform in platform_names:
        folder = os.path.join(out_dir, platform)
        os.makedirs(folder, exist_ok=True)
        # delete all files in folders
        for path in os.listdir(folder):
            file = os.path.join(folder, path)
            if os.path.isfile(file) and path not in [
                ".terraform.lock.hcl",
                "terraform.tfstate",
                ".terraform.tfstate.lock.info",
                "terraform.tfstate.backup",
            ]:
                os.remove(file)

    # read templates
    logger.info("Reading templates...")
    template_registry: dict[str, TemplateDefinition] = {}
    for template in root["templates"]:
        template_name = template.replace("/", "")
        template_registry[template_name] = read_template_dir(
            template_dir, template_name, template, schema_registry
        )

    # write out templated files
    logger.info("Generating output files...")
    for platform_struct in platforms:
        platform_name = platform_struct["name"]
        platform_properties = platform_struct["properties"]

        component_data = template_data | platform_properties

        folder = os.path.join(out_dir, platform_name)
        os.makedirs(folder, exist_ok=True)

        for special in ["main", "versions"]:
            files = read_template_dir(
                template_dir, special, root[special], schema_registry
            ).render(platform_name, jinja, component_data)
            for file in files:
                path = file.save(folder, special)
                mappings.append(
                    {
                        "platform": platform_name,
                        "component": special,
                        "path": path,
                        "properties": component_data,
                    }
                )
                stats["outputFiles"] = stats["outputFiles"] + 1

    for component in architecture.components():
        if component["type"] not in template_registry:
            logger.error(f"Unknown component type '{component['type']}'")
            exit(1)

        template: TemplateDefinition = template_registry[component["type"]]
        component_name = component["name"]
        component_properties = component.get("properties")

        # validate that all required component properties are set
        if not template.validate_properties(component_properties):
            logger.error(f"Invalid properties for component '{component_name}'")
            exit(1)

        component_data = (
            template_data
            | platform_properties
            | component_properties
            | {
                "resourceId": component_name,
                "resourceType": component["type"],
            }
        )

        for platform_struct in platforms:
            platform_name = platform_struct["name"]
            platform_properties = platform_struct["properties"]

            folder = os.path.join(out_dir, platform_name)
            files = template.render(platform_name, jinja, component_data)
            for file in files:
                path = file.save(folder, component["name"])

                mappings.append(
                    {
                        "platform": platform_name,
                        "component": component["name"],
                        "path": path,
                        "properties": component_data,
                    }
                )
                stats["outputFiles"] = stats["outputFiles"] + 1

    if report:
        if not debug:
            logger.info("Prettifying report...")
            platform_mappings = {}
            for mapping in mappings:
                del mapping["properties"]
                plat = mapping["platform"]

                del mapping["platform"]
                if plat in platform_mappings:
                    platform_mappings[plat].append(mapping)
                else:
                    platform_mappings[plat] = [mapping]

            mappings = platform_mappings

        logger.info("Saving report...")
        with open("out/report.yaml", "w", encoding="utf8") as file:
            file.write(
                yaml.dump(
                    {
                        "metadata": architecture.metadata,
                        "stats": stats,
                        "platforms": platform_names,
                        "mappings": mappings,
                    },
                    Dumper=get_report_dumper(),
                )
            )
