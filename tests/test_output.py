from pathlib import Path
from unittest.mock import patch

from freezegun import freeze_time

from transidate.outputs import ConsoleOutput, CSVOutput, Output
from transidate.validators import ValidationResult
from transidate.violations import Violation


@freeze_time("2020-01-14 12:12:12")
def test_output_class(txc24):
    result = ValidationResult(status=ValidationResult.ERROR, violations=[])
    o = Output(dataset=txc24, result=result)

    exp_extension = ".txt"
    exp_dataset_name = "txc24good_xml"
    exp_datetime = "_2020_01_14_12_12_12"
    exp_output_path = Path.cwd() / (exp_dataset_name + exp_datetime + exp_extension)

    assert o.get_extension() == exp_extension
    assert o.dataset_name == exp_dataset_name
    assert o.get_stem() == exp_dataset_name + exp_datetime
    assert o.get_output_path() == Path.cwd() / exp_output_path


def test_csv_output(txc24):
    result = ValidationResult(status=ValidationResult.ERROR, violations=[])
    o = CSVOutput(dataset=txc24, result=result)
    assert o.get_extension() == ".csv"


@patch("transidate.outputs.console")
def test_console_output(mconsole, txc21):
    violation = Violation(
        filename=txc21.path.name, line=24, message="Violation occurred"
    )
    result = ValidationResult(status=ValidationResult.ERROR, violations=[violation])
    o = ConsoleOutput(dataset=txc21, result=result)
    o.output()
    expected_output = f"{violation.filename}:{violation.line}: {violation.message}"
    mconsole.print.assert_called_once_with(expected_output)
