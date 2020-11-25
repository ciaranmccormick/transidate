from typing import List

from prettytable import PrettyTable  # type: ignore
from transidate.validators import ValidationError


class ErrorTable:
    field_names = ["Line", "Element", "Details"]

    def __init__(self, errors: List[ValidationError]):
        self.errors = errors
        self.table = PrettyTable()
        self.table.field_names = self.field_names
        self.table.align = "l"

    def pretty_errors(self) -> str:
        for error in self.errors:
            self.table.add_row(
                [error.line, error.message.element, error.message.details]
            )

        return self.table.get_string()
