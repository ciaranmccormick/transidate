from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional

from lxml import etree
from transidate.constants import NETEX_XSD_URLS, SIRI_XSD_URLS, TXC_XSD_URLS
from transidate.typing import XMLSchema
from transidate.violations import Violation, ViolationProcessor
from transidate.xsd import Config, DownloaderFactory


@dataclass
class ValidationError:
    filename: str
    line: int
    message: Violation
    type_name: str


@dataclass
class ValidationResult:
    OK = 0
    ERROR = -1

    filename: str
    status: int
    data_type: Optional[str]
    version: str
    errors: List[ValidationError]


class DocumentType(Enum):
    Other = -1
    TransXChange = 0
    NeTEx = 1
    Siri = 2


class XMLValidator:
    version_key: Optional[str] = None
    name: Optional[str] = None

    def __init__(self, source):
        if hasattr(source, "seek"):
            source.seek(0)
        self._source = source
        self._tree = etree.parse(source)

    def __repr__(self):
        return f"{self.__class__.__name__}(souce={self._source!r})"

    @property
    def filename(self):
        if hasattr(self._source, "filename"):
            return self._source.filename
        elif hasattr(self._source, "name"):
            return self._source.name
        else:
            return self._source

    @property
    def version(self) -> str:
        """Get the schema version of the document."""
        root = self._tree.getroot()
        if self.version_key is None:
            raise ValueError

        return root.get(self.version_key, "")

    def get_config(self) -> Config:
        raise NotImplementedError

    def validate(self, schema: Optional[XMLSchema] = None) -> ValidationResult:
        """Validate an XML file."""
        errors = []
        status = ValidationResult.OK
        if schema is None:
            config = self.get_config()
            factory = DownloaderFactory(config)
            downloader = factory.get_downloader()
            schema = downloader.download()

        try:
            schema.assertValid(self._tree)
        except etree.DocumentInvalid as exc:
            processor = ViolationProcessor()
            status = ValidationResult.ERROR
            errors = [
                ValidationError(
                    message=processor.process(entry.message),
                    filename=Path(entry.filename).name,
                    type_name=entry.type_name,
                    line=entry.line,
                )
                for entry in exc.error_log
            ]

        return ValidationResult(
            filename=self.filename,
            status=status,
            errors=errors,
            version=self.version,
            data_type=self.name,
        )


class TransXChangeValidator(XMLValidator):
    version_key = "SchemaVersion"
    name = "TransXChange"

    def get_config(self) -> Config:
        root = Path("TransXChange_general.xsd")
        url = TXC_XSD_URLS.get(self.version, "")
        return Config(url, root)


class NeTExValidator(XMLValidator):
    version_key = "version"
    name = "NeTEx"

    def get_config(self) -> Config:
        root = Path("xsd").joinpath("NeTEx_publication.xsd")
        url = NETEX_XSD_URLS.get(self.version, "")
        return Config(url, root)


class SiriValidator(XMLValidator):
    version_key = "version"
    name = "Siri"

    def get_config(self) -> Config:
        root = Path("xsd").joinpath("siri.xsd")
        url = SIRI_XSD_URLS.get(self.version, "")
        return Config(url, root)


class ValidatorFactory:
    def __init__(self, source):
        self._source = source
        self._tree = etree.parse(source)

    def get_validator(self) -> XMLValidator:
        root = self._tree.getroot()
        nsmap = root.nsmap.get(None)

        if "netex" in nsmap.lower():
            return NeTExValidator(self._source)
        elif "siri" in nsmap.lower():
            return SiriValidator(self._source)
        return TransXChangeValidator(self._source)
