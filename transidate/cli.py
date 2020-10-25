from pathlib import Path

import click
from transidate.xml import ValidationResult, XMLDocument
from transidate.zip import ZipValidator


@click.group()
def cli():
    pass


def print_results(result: ValidationResult):
    if result.status == ValidationResult.ERROR:
        click.echo("")
        click.echo("Errors found.")
        click.echo("=============")
        click.echo(result.error)
    else:
        click.echo(
            f"{result.filename} is a valid {result.data_type} "
            f"v{result.version} file."
        )


def validate_xml_file(fullpath: str):
    doc = XMLDocument(fullpath)
    click.echo(f"Validating {fullpath}.")
    result = doc.validate()
    print_results(result)


def validate_zip_file(fullpath: str):
    with open(fullpath, "rb") as f_:
        validator = ZipValidator(f_)
        for result in validator.validate_files():
            print_results(result)


@cli.command()
@click.argument("source")
def validate(source: str):
    fullpath = str(Path(source).absolute())

    if fullpath.endswith(".xml"):
        validate_xml_file(fullpath)
    elif fullpath.endswith(".zip"):
        validate_zip_file(fullpath)
    else:
        click.echo(f"Can't validate {fullpath}.")
