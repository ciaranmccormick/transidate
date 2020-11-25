import io
import logging
import tempfile
import zipfile
from abc import abstractmethod
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
        raise NotSupported("'source' is not a valid XMLSource.")
    schema = etree.XMLSchema(doc)
    return schema


@dataclass
class Config:
    url: str
    root: Path


class Downloader:
    def __init__(self, source, root=None):
        self.source = source
        self.root = root

    @classmethod
    def from_config(cls, config):
        return cls(config.url, config.root)

    @abstractmethod
    def download(self) -> XMLSchema:
        pass


class XMLDownloader(Downloader):
    def download(self) -> XMLSchema:
        return get_xsd(self.source)


class ZipDownloader(Downloader):
    def download(self) -> XMLSchema:
        assert self.root is not None
        response = requests.get(self.source)
        with tempfile.TemporaryDirectory() as tempdir:
            with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
                zf.extractall(tempdir)
                rootfile = Path(tempdir) / self.root
                return get_xsd(str(rootfile))


class DownloaderFactory:
    XSD = ".xsd"
    ZIP = ".zip"

    def __init__(self, config: Config):
        self.config = config

    def get_downloader(self) -> Downloader:
        if self.config.url.endswith(self.XSD):
            return XMLDownloader.from_config(self.config)
        else:
            return ZipDownloader.from_config(self.config)
