import configparser
import io
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, KeysView, List, Optional

import requests
from lxml import etree

from transidate.console import console
from transidate.datasets import DataSet
from transidate.exceptions import NotRegistered, NotSupported
from transidate.violations import Violation


@dataclass
class ValidationResult:
    OK = 0
    ERROR = -1

    status: int
    violations: List[Violation]


class Validator:
    def __init__(self, url: str, root_path: str):
        self.url = url
        self.root_path = root_path
        self._schema: Optional[etree.XMLSchema] = None

    def get_xsd(self, schema_path: Path) -> etree.XMLSchema:
        paths = [p for p in schema_path.glob("**/" + self.root_path)]
        try:
            fullpath = paths[0]
            console.print(f"Parsing schema file {self.root_path}.")
            doc = etree.parse(fullpath.as_posix())
            schema = etree.XMLSchema(doc)
        except OSError:
            raise NotSupported(f"Source {self.root_path!r} cannot be parsed.")
        except IndexError:
            raise NotSupported(f"Could not find {self.root_path!r} in schema directory")
        except etree.XMLSchemaParseError as exc:
            raise NotSupported(str(exc))
        return schema

    @property
    def schema(self) -> etree.XMLSchema:
        if self._schema:
            return self._schema

        console.print(f"Fetching schema from {self.url}.", overflow="ellipsis")
        response = requests.get(self.url)
        with tempfile.TemporaryDirectory() as tempdir:
            with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
                console.print(f"Extracting schema to {tempdir}.")
                zf.extractall(tempdir)
                self._schema = self.get_xsd(Path(tempdir))
        return self._schema

    def validate(self, dataset: DataSet) -> ValidationResult:
        violations = []
        status = ValidationResult.OK
        for d in dataset.documents():
            console.print(f"Validating {d.name}.")
            try:
                self.schema.assertValid(d.tree)
            except etree.DocumentInvalid:
                status = ValidationResult.ERROR
                errors = self.schema.error_log  # type: ignore
                violations += [Violation.from_log_entry(e) for e in errors]
            except etree.XMLSyntaxError as exc:
                status = ValidationResult.ERROR
                violations.append(Violation.from_syntax_error(exc))

        return ValidationResult(status=status, violations=violations)


class ValidatorFactory:
    def __init__(self):
        self._validators: Dict[str, Validator] = {}

    def register_schema(self, key: str, url: str, root_path: str) -> None:
        self._validators[key] = Validator(url=url, root_path=root_path)

    def get_validator(self, key: str) -> Validator:
        validator = self._validators.get(key, None)
        if validator is None:
            raise NotRegistered(f"Schema {key!r} was not registered.")

        # Download the schema immediately
        # validator.schema
        return validator

    @property
    def registered_schemas(self) -> KeysView[str]:
        return self._validators.keys()

    def _add_from_config(self, config: configparser.ConfigParser) -> None:
        for key in config.sections():
            section = config[key]
            url = section.get("url")
            root = section.get("root")
            self.register_schema(key=key, url=url, root_path=root)

    @classmethod
    def from_config(cls, path: Path):
        factory = cls()
        with path.open("r") as f:
            config = configparser.ConfigParser()
            config.read_file(f)
        factory._add_from_config(config)
        return factory


default_config = Path(__file__).parent / "default.ini"
Validators = ValidatorFactory.from_config(default_config)
