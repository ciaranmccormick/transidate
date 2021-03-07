from typing import IO, TextIO, Union

from lxml import etree

XMLSchema = etree.XMLSchema
XMLFile = Union[TextIO, IO[bytes]]
