from configparser import ConfigParser
from pathlib import Path
from typing import Union

import click
from click.exceptions import ClickException

from transidate.console import console
from transidate.datasets import DataSet
from transidate.exceptions import TransidateException
from transidate.outputs import ConsoleOutput, CSVOutput
from transidate.validators import ValidationResult, Validator, Validators

_SCHEMA_TYPES = Validators.registered_schemas
HEADER = "[bold red]"


def _load_schemas(path: Union[Path, str]):
    if isinstance(path, str):
        path = Path(path)
    with path.open("r") as f:
        config = ConfigParser()
        config.read_file(f)
    Validators._add_from_config(config)


def _validate(validator: Validator, dataset: DataSet) -> ValidationResult:
    console.rule(HEADER + "Validating Documents")
    try:
        result = validator.validate(dataset)
    except TransidateException as exc:
        console.rule(HEADER + "Error")
        raise ClickException(str(exc))
    else:
        return result


@click.group()
def cli():
    pass


@cli.command()
@click.argument("source", type=click.Path(exists=True))
@click.option(
    "--version",
    help="Version of schema to validate against.",
    type=str,
    default="TXC2.4",
)
@click.option(
    "--csv/--no-csv", "output_csv", help="Write violations to csv.", default=False
)
@click.option(
    "--schemas",
    help="Path to configuration file containing other schemas.",
    type=click.Path(exists=True),
)
def validate(source: str, version: str, output_csv: bool, schemas: Path):
    """
    Validate a transit data file against a specified schema.
    """
    if schemas:
        _load_schemas(schemas)

    try:
        validator = Validators.get_validator(version)
    except TransidateException as exc:
        console.rule(HEADER + "Error")
        raise ClickException(str(exc))

    dataset_path = Path(source)
    dataset = DataSet(dataset_path)
    result = _validate(validator, dataset)

    if result.status == ValidationResult.OK:
        console.rule(HEADER + "Results")
        console.print("No issues found.")
    else:
        console.rule(HEADER + f"Results: {len(result.violations)} Issues found")
        ConsoleOutput(dataset=dataset, result=result).output()
        if output_csv:
            CSVOutput(dataset=dataset, result=result).output()


@cli.command()
@click.option(
    "--schemas",
    help="Path to configuration file containing other schemas.",
    type=click.Path(exists=True),
)
def list(schemas: Path):
    """
    Lists all the schemas that transidate can validate a data set against.
    """
    if schemas:
        _load_schemas(schemas)

    console.rule(HEADER + "Available Schemas")
    for name in Validators.registered_schemas:
        validator = Validators.get_validator(name)
        console.print(f"{name}: {validator.url}")
