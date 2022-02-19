Multiform - A Multi-Cloud Templating System
====

A templating system that helps to manage [Terraform](https://www.terraform.io/) deployments in [multi-cloud](https://www.cloudflare.com/learning/cloud/what-is-multicloud/) environments.

## About this Project

This command-line tool allows transforming a generic (platform-independent) cloud architecture into Terraform deployments that target different platforms. While [Terraform exposes the full functionality and provides a "single common denominator"](https://www.terraform.io/language/modules/develop/composition#multi-cloud-abstractions), this tool aims to provide an interface for only the common functionality to abstract platform-specific knowledge away.

This repo contains an [example architecture](example/architecture.yaml) together with [templates](example/templates/) required for this architecture. This architecture describes the required infrastructure for a [serverless](https://www.cloudflare.com/learning/serverless/what-is-serverless/) web application. Deployments for each platform (that the templates in this repo are based on), as well as the files for the FaaS code and website, can be found in this [repository](https://github.com/michidk/serverless-webapp/).

## Contents

The relevant parts of this repository are:

| Folder/File | Description |
| ----------- | ----------- |
| [.devcontainer/](.devcontainer) | The [vscode devcontainer](https://code.visualstudio.com/docs/remote/containers) for this project |
| [.github/](.github/) | Reamd resources |
| [.vscode/](.vscode/) | [vscode](https://code.visualstudio.com/) settings |
| [example/](example/) | The serverless webapp sample |
| [src/](src/) | The Python source code of the tool |
| [justfile](justfile) | The just configuration |

## How it works

This tool parses [Jinja](https://palletsprojects.com/p/jinja/) templates and instantiates the according to the architecture file. This file is a YAML file that generically describes the required cloud infrastructure. The templates have definition (YAML) files that describe the structure, inputs and platforms to the Terraform-Jinja (`.tf.j2`) templates. All YAML files are validated with [Cerberus](https://docs.python-cerberus.org/en/stable/) schemes.

Example architecture file:

```yaml
kind: Architecture
metadata:
  name: simple-web-service
spec:
  platforms:
    - name: aws
      properties:
        region: us-east-1
  components:
    - name: backend-code
      type: object-storage
      properties:
        uniqueName: 23423-faas-files
    - name: backend-faas
      type: function
      properties:
        uniqueName: 23423455-faas-backend
        language: javascript
        source:
          bucket: !ref backend-code
          object: function.zip
```

## Setup & Quickstart

This repository uses [just](https://github.com/casey/just/) - which is a command runner utility similar to make. Either use just (installed in this devcontainer) or look up the command in the [justfile](justfile).

Install with `just install` and then use `multiform` command-line interface.
To run the example use `just run` to run the transpiler on the [example](example/).

## Usage

The `-h` flag is available for all `multiform` commands.

The `-v` flag is used to set the verbosity level (see help for more info).

There are two main subcommands: `transpile` and `plot`.
`multiform transpile` provides a CLI to the transpiler, while `multiform plot` generates a graph of the provided architecture.

### Transpile

The `multiform transpile` command can be used to transpile a generic architecture file together with a set of templates to platform-specific Terraform files.
`multiform transpile -h` will show the help for the transpiler.

The following flags are available:

| Flag | Description |
| ---- | ----------- |
| `-a <file>` | The architecture file to use |
| `-t <folder>` | The folder that contains all templates and the `root.yaml` file |
| `-o <folder>` | The folder where the outputs should be stored in |
| `-r` | Will generate a `report.yaml` file that contains additional information about the transpilation |
| `-d` | Will add debug information to the report |

### Plot

The `multiform plot` command can be used to generate a graph of the architecture file.
`multiform plot -h` will show the help for the transpiler.

The following flags are available:

| Flag | Description |
| ---- | ----------- |
| `-a <file>` | The architecture file to use |
| `-o <file>` | The output file |
| `-f <format>` | Will output the graph in the given format (see help for options) |
