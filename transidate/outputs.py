import csv
from datetime import datetime
from pathlib import Path

from transidate.console import console
from transidate.datasets import DataSet
from transidate.results import BaseResult


class Output:
    def __init__(self, dataset: DataSet, result: BaseResult):
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
        for item in self.result.items:
            console.print(f"{item.filename}:{item.line}: {item.message}")


class CSVOutput(Output):
    def get_extension(self) -> str:
        return ".csv"

    def _write_csv(self, writer: csv.DictWriter) -> None:
        items = [v.dict() for v in self.result.items]
        writer.writeheader()
        writer.writerows(items)

    def output(self) -> None:
        output_path = self.get_output_path()
        console.print(f"Outputing CSV to {output_path.as_posix()}")
        with output_path.open("w") as f:
            headers = ["filename", "line", "message"]
            writer = csv.DictWriter(f, fieldnames=headers)
            self._write_csv(writer)
