from functools import partial
from pathlib import Path

import click
import emoji
from transidate.tables import ErrorTable
from transidate.validators import ValidationResult, ValidatorFactory
from transidate.zip import ZipValidator

emojize = partial(emoji.emojize, use_aliases=True)


@click.group()
def cli():
    pass


def print_results(result: ValidationResult):
    if result.status == ValidationResult.ERROR:
        table = ErrorTable(result.errors)
        click.echo("")
        click.echo(emojize(f":poop: {result.filename}"))
        click.echo(table.pretty_errors())
    else:
        click.echo(emojize(f":white_check_mark: {result.filename}"))


def validate_xml_file(fullpath: str):
    factory = ValidatorFactory(fullpath)
    validator = factory.get_validator()
    click.echo(emojize(f":page_facing_up: {validator.filename}"))
    result = validator.validate()
    print_results(result)
    click.echo(emojize(":sparkles: Done :sparkles:"))


def validate_zip_file(fullpath: str):
    with open(fullpath, "rb") as f_:
        validator = ZipValidator(f_)
        click.echo(emojize(f":open_file_folder: {fullpath}"))
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
