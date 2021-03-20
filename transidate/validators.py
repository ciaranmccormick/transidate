import io
import zipfile
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
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
    """
    Class for validating an XML file against an XML Schema.

    Args:
        url: The url of where the schema can be downloaded from.
        root_path: The path to the root file of the schema.
    """

    def __init__(self, url: str, root_path: str):
        self.url = url
        self.root_path = root_path
        self._schema: Optional[etree.XMLSchema] = None

    def _download_schema(self) -> bytes:
        """
        Download a schema zip file.

        Args:
            None
        Returns:
            A byte string representation of the schema zip file.
        """
        console.print(f"Fetching schema from {self.url}.", overflow="ellipsis")
        response = requests.get(self.url)
        return response.content

    def _extract_zip(self, content: bytes, savepath: Path):
        """
        Extracts a zip byte string to a specified save location.

        Args:
            content: byte string representation of a zipped schema.
            savepath: Path where the zip is extracted to.

        Returns:
            None
        """
        console.print(f"Extracting schema to {savepath}.")
        with zipfile.ZipFile(io.BytesIO(content)) as zf:
            zf.extractall(savepath)

    def _get_document(self, savepath: Path) -> etree._ElementTree:
        """
        Get an ElmentTree from a path.

        Args:
            savepath: The Path where the XML document is saved.

        Returns:
            ElementTree of the XML document.
        """
        try:
            console.print(f"Parsing schema file {self.root_path}.")
            fullpath = savepath / self.root_path
            doc = etree.parse(fullpath.as_posix())
        except OSError:
            raise NotSupported(f"Source {self.root_path!r} cannot be parsed.")
        else:
            return doc

    def _get_schema(self) -> etree.XMLSchema:
        """
        Get an XMLSchema.

        Returns:
            XMLSchema for this validator.
        """
        content = self._download_schema()
        with TemporaryDirectory() as tempdir:
            savepath = Path(tempdir)
            self._extract_zip(content, savepath)
            doc = self._get_document(savepath=savepath)
            schema = etree.XMLSchema(doc)
            return schema

    @property
    def schema(self) -> etree.XMLSchema:
        if self._schema:
            return self._schema
        self._schema = self._get_schema()
        return self._schema

    def validate(self, dataset: DataSet) -> ValidationResult:
        """
        Validates a DataSet against a schema.

        Args:
            dataset: The DataSet to validate.

        Returns:
            ValidationResult detailing the outcome of the validation.
        """
        violations = []
        status = ValidationResult.OK
        for d in dataset.documents():
            console.print(f"Validating {d.name}.")
            try:
                success = self.schema.validate(d.tree)  # type: ignore
            except etree.XMLSyntaxError as exc:
                status = ValidationResult.ERROR
                violations.append(Violation.from_syntax_error(exc))
            else:
                if not success:
                    status = ValidationResult.ERROR
                    errors = self.schema.error_log  # type: ignore
                    violations += [Violation.from_log_entry(e) for e in errors]

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
