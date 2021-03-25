from enum import IntEnum
from pathlib import Path
from typing import List

from lxml import etree
from pydantic import BaseModel


class Status(IntEnum):
    ok = 0
    error = -1


class BaseItem(BaseModel):
    line: int
    message: str
    filename: str


class BaseResult(BaseModel):
    status: Status = Status.ok
    items: List[BaseItem]

    @property
    def item_count(self):
        return len(self.items)


class Evaluation(BaseItem):
    pass

    @classmethod
    def from_element(cls, element: etree._Element):
        filename = Path(element.base).name  # type: ignore
        line = element.sourceline  # type: ignore
        text = element.text if not None else element.tag
        return cls(line=line, filename=filename, message=text)


class EvaluationResult(BaseResult):
    pass


class Violation(BaseItem):
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


class ValidationResult(BaseResult):
    pass
