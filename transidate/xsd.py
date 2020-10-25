import io
import logging
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path

import requests
from lxml import etree
from transidate.exceptions import NotSupported
from transidate.typing import XMLSchema, XMLSource

logger = logging.getLogger(__name__)


def get_xsd(source: XMLSource) -> XMLSchema:
    try:
        doc = etree.parse(source)
    except OSError:
        raise NotSupported
    schema = etree.XMLSchema(doc)
    return schema


@dataclass
class XSDConfig:
    url: str
    root: Path


class XSDDownloader:
    XSD = "xsd"
    ZIP = "zip"

    def __init__(self, source, root=None):
        self.source = source
        self.root = root

    @classmethod
    def from_xsd_config(cls, config):
        return cls(config.url, config.root)

    def download_xsd(self) -> XMLSchema:
        if self.source.endswith(self.XSD):
            return self._load_from_source()
        else:
            return self._load_from_zip()

    def _load_from_source(self) -> XMLSchema:
        return get_xsd(self.source)

    def _load_from_zip(self) -> XMLSchema:
        assert self.root is not None
        response = requests.get(self.source)
        with tempfile.TemporaryDirectory() as tempdir, zipfile.ZipFile(
            io.BytesIO(response.content)
        ) as zf:
            zf.extractall(tempdir)
            rootfile = Path(tempdir) / self.root
            return get_xsd(str(rootfile))
