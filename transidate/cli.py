from pathlib import Path

import click

from transidate.console import console
from transidate.datasets import DataSet
from transidate.evaluators import XPathEvaluator
from transidate.outputs import ConsoleOutput, CSVOutput
from transidate.results import Status
from transidate.validators import Validators

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
    console.rule(header + "Downloading Schema")
    schema = Validators.get_validator(version)

    console.rule(header + "Validating Documents")
    dataset_path = Path(source)
    dataset = DataSet(dataset_path)

    result = schema.validate(dataset)
    ok = result.status == Status.ok

    if ok:
        console.rule(header + "Results")
        console.print("No issues found.")
    else:
        issue = "issues" if result.item_count > 1 else "issue"
        console.rule(header + f"Results: {result.item_count} {issue} found")
        ConsoleOutput(dataset=dataset, result=result).output()
        if output_csv:
            CSVOutput(dataset=dataset, result=result).output()


@cli.command()
@click.argument("source", type=click.Path(exists=True))
@click.argument("expression", type=str)
@click.option(
    "--version",
    help="Version of schema to validate against.",
    type=click.Choice(_SCHEMA_TYPES, case_sensitive=False),
    default="TXC2.4",
)
@click.option(
    "--namespace",
    help="The symbol to use in the xpath to represent the namespace.",
    type=str,
    default="x",
)
def xpath(expression: str, source: str, version: str, namespace: str):
    """
    Run an xpath expression against an XML file.
    """
    header = "[bold red]"
    console.rule(header + "Evaluating XPath Expression")

    dataset_path = Path(source)
    dataset = DataSet(dataset_path)
    evaluator = XPathEvaluator(expression, namespace)
    result = evaluator.evaluate(dataset)

    ok = result.status == Status.ok
    if not ok:
        console.rule(header + "Results")
        console.print("You did not supply I valid XPath expression.")
    elif len(result.items) == 0:
        console.rule(header + "Results")
        console.print("Expression didn't return any results.")
    else:
        value = "values" if result.item_count > 1 else "value"
        console.rule(header + f"Results: {result.item_count} {value} found")
        ConsoleOutput(dataset=dataset, result=result).output()
