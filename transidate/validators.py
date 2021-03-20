import io
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, KeysView, List, Optional

import requests
from lxml import etree

from transidate.console import console
from transidate.constants import (
    NETEX110_URL,
    NETEX_ROOT,
    SIRI10_URL,
    SIRI13_URL,
    SIRI14_URL,
    SIRI20_URL,
    SIRI_ROOT,
    TXC21_URL,
    TXC24_URL,
    TXC_ROOT,
)
from transidate.datasets import DataSet
from transidate.exceptions import NotSupported
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
        fullpath = schema_path / self.root_path
        try:
            console.print(f"Parsing schema file {self.root_path}.")
            doc = etree.parse(fullpath.as_posix())
        except OSError:
            raise NotSupported(f"Source {self.root_path!r} cannot be parsed.")
        schema = etree.XMLSchema(doc)
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
            raise ValueError(f"Schema {key!r} was not registered.")

        # Download the schema immediately
        validator.schema
        return validator

    @property
    def registered_schemas(self) -> KeysView[str]:
        return self._validators.keys()


Validators = ValidatorFactory()  # type: ignore
Validators.register_schema("TXC2.1", url=TXC21_URL, root_path=TXC_ROOT)
Validators.register_schema("TXC2.4", url=TXC24_URL, root_path=TXC_ROOT)
Validators.register_schema("SIRI1.1", url=SIRI10_URL, root_path=SIRI_ROOT)
Validators.register_schema("SIRI1.3", url=SIRI13_URL, root_path=SIRI_ROOT)
Validators.register_schema("SIRI1.4", url=SIRI14_URL, root_path=SIRI_ROOT)
Validators.register_schema("SIRI2.0", url=SIRI20_URL, root_path="xsd/" + SIRI_ROOT)
Validators.register_schema("NETEX1.0", url=NETEX110_URL, root_path=NETEX_ROOT)
Validators.register_schema("NETEX1.10", url=NETEX110_URL, root_path=NETEX_ROOT)
