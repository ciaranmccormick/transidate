from pathlib import Path

import click
from transidate.console import console
from transidate.datasets import DataSet
from transidate.outputs import ConsoleOutput, CSVOutput
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
@click.option(
    "--csv/--no-csv", "output_csv", help="Write violations to csv.", default=False
)
def validate(source: str, version: str, output_csv: bool):
    """
    Validate a transit data file against a specified schema.
    """
    header = "[bold red]"
    breakpoint()

    console.rule(header + "Downloading Schema")
    schema = Validators.get_validator(version)

    console.rule(header + "Validating Documents")
    dataset_path = Path(source)
    dataset = DataSet(dataset_path)

    result = schema.validate(dataset)
    ok = result.status == ValidationResult.OK

    if ok:
        console.rule(header + "Results")
        console.print("No issues found.")
    else:
        console.rule(header + f"Results: {len(result.violations)} Issues found")
        ConsoleOutput(dataset=dataset, result=result).output()
        if output_csv:
            CSVOutput(dataset=dataset, result=result).output()
