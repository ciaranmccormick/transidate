import zipfile
from pathlib import Path
from typing import Iterator

from lxml import etree
from transidate.typing import XMLFile


class Document:
    def __init__(self, source: XMLFile):
        self.source = source

    @property
    def file(self) -> XMLFile:
        self.source.seek(0)
        return self.source

    @property
    def name(self) -> str:
        return self.source.name

    @property
    def tree(self) -> etree._ElementTree:
        return etree.parse(self.file)


class DataSet:
    def __init__(self, path: Path):
        self.path: Path = path

    @property
    def is_zip(self) -> bool:
        return self.path.suffix == ".zip"

    def documents(self) -> Iterator[Document]:
        if self.is_zip:
            with zipfile.ZipFile(self.path.as_posix()) as zf:
                xml_files = [n for n in zf.namelist() if n.endswith(".xml")]
                for name in xml_files:
                    with zf.open(name, "r") as f:
                        yield Document(f)
        else:
            with self.path.open("r") as xmlfile:
                yield Document(xmlfile)
