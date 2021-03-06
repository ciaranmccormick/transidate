import io
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, KeysView, List, Optional

import requests
from lxml import etree
from transidate.console import console
from transidate.constants import NAPTAN_URL, NETEX_URL, SIRI_URL
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
        fullpath = schema_path.joinpath(self.root_path).as_posix()
        try:
            console.print(f"Parsing schema file {self.root_path}.")
            doc = etree.parse(fullpath)
        except OSError:
            raise NotSupported(f"{fullpath!s} is not a valid XMLSource.")
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
                violations += [
                    Violation.from_log_entry(e) for e in self.schema.error_log
                ]
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
            raise ValueError(f"Schema {key!s} was not registered.")

        # Download the schema immediately
        validator.schema
        return validator

    @property
    def registered_schemas(self) -> KeysView[str]:
        return self._validators.keys()


Validators = ValidatorFactory()  # type: ignore
Validators.register_schema(
    "TXC2.1",
    url=NAPTAN_URL + "2.1/TransXChange_schema_2.1.zip",
    root_path="TransXChange_general.xsd",
)
Validators.register_schema(
    "TXC2.4",
    url=NAPTAN_URL + "2.4/TransXChange_schema_2.4.zip",
    root_path="TransXChange_general.xsd",
)
Validators.register_schema(
    "SIRI1.1", url=SIRI_URL + "1.0/siri-1.0.zip", root_path="siri.xsd"
)
Validators.register_schema(
    "SIRI1.3", url=SIRI_URL + "1.3/siri-1.3.zip", root_path="siri.xsd"
)
Validators.register_schema(
    "SIRI1.4", url=SIRI_URL + "1.4/siri-1.4.zip", root_path="siri.xsd"
)
Validators.register_schema(
    "SIRI2.0", url=SIRI_URL + "2.0/Siri_XML-v2.0.zip", root_path="xsd/siri.xsd"
)
Validators.register_schema(
    "NETEX1.0",
    url=NETEX_URL + "1.10/NeTExXmlSchemaOnly-v1.10_2020.07.29.zip",
    root_path="xsd/NeTEx_siri.xsd",
)
Validators.register_schema(
    "NETEX1.10",
    url=NETEX_URL + "1.10/NeTExXmlSchemaOnly-v1.10_2020.07.29.zip",
    root_path="xsd/NeTEx_siri.xsd",
)
