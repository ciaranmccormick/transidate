from pathlib import Path

from lxml import etree
from pydantic.main import BaseModel


class Violation(BaseModel):
    line: int
    message: str
    filename: str

    @classmethod
    def from_log_entry(cls, entry: etree._LogEntry):
        filename = Path(entry.filename).name
        return cls(line=entry.line, message=entry.message, filename=filename)

    @classmethod
    def from_syntax_error(cls, entry: etree.XMLSyntaxError):
        filename = ""
        if entry.filename is not None:
            filename = Path(entry.filename).name
        return cls(line=entry.lineno, message=entry.msg, filename=filename)
