import csv
from datetime import datetime
from pathlib import Path

from transidate.console import console
from transidate.datasets import DataSet
from transidate.validators import ValidationResult


class Output:
    def __init__(self, dataset: DataSet, result: ValidationResult):
        self.dataset = dataset
        self.result = result

    @property
    def dataset_name(self) -> str:
        """Name of the dataset with the `.` replaced with `_`."""
        return self.dataset.path.name.replace(".", "_")

    def get_stem(self) -> str:
        """Returns a filename for the output file minus the extension."""
        now = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        return self.dataset_name + "_" + now

    def get_extension(self) -> str:
        """Returns an extension with a leading `.`."""
        return ".txt"

    def get_output_path(self) -> Path:
        """Returns a full output path minus the file extension."""
        filename = self.get_stem() + self.get_extension()
        return Path.cwd() / filename


class ConsoleOutput(Output):
    def output(self) -> None:
        for violation in self.result.violations:
            console.print(f"{violation.filename}:{violation.line}: {violation.message}")


class CSVOutput(Output):
    def get_extension(self) -> str:
        return ".csv"

    def _write_csv(self, writer: csv.DictWriter) -> None:
        violations = [v.dict() for v in self.result.violations]
        writer.writeheader()
        writer.writerows(violations)

    def output(self) -> None:
        output_path = self.get_output_path()
        console.print(f"Outputing CSV to {output_path.as_posix()}")
        with output_path.open("w") as f:
            headers = ["filename", "line", "message"]
            writer = csv.DictWriter(f, fieldnames=headers)
            self._write_csv(writer)
