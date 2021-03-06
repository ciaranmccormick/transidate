from pathlib import Path

import click
from transidate.console import console
from transidate.datasets import DataSet
from transidate.validators import ValidationResult, Validators

_SCHEMA_TYPES = Validators.registered_schemas


@click.group()
def cli():
    pass


@cli.command()
@click.argument("source", type=click.Path(exists=True))
@click.option(
    "--version",
    help="Version of schema to validate against.",
    type=click.Choice(_SCHEMA_TYPES, case_sensitive=False),
    default="TXC2.4",
)
def validate(source: str, version: str):
    """
    Validate a transit data file against a specified schema.
    """
    header = "[bold red]"
    console.rule(header + "Downloading Schema")
    schema = Validators.get_validator(version)

    console.rule(header + "Validating Documents")
    dataset = DataSet(Path(source))

    result = schema.validate(dataset)
    ok = result.status == ValidationResult.OK

    if ok:
        console.rule(header + "Results")
        console.print("No issues found.")
    else:
        console.rule(header + f"Results: {len(result.violations)} Issues found")
        for violation in result.violations:
            console.print(f"{violation.filename}:{violation.line}: {violation.message}")
