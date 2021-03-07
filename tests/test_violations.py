from unittest.mock import Mock

import pytest
from lxml.etree import XMLSyntaxError, _LogEntry

from transidate.violations import Violation


@pytest.mark.parametrize(
    "filepath, expected_filename", [("/a/b/file.xml", "file.xml"), (None, "")]
)
def test_violation_from_syntax_error(filepath, expected_filename):
    error = Mock(spec=XMLSyntaxError, filename=filepath, lineno=23, msg="A message")
    actual = Violation.from_syntax_error(error)
    expected = Violation(line=23, filename=expected_filename, message="A message")
    assert actual == expected


def test_violation_from_log_entry():
    error = Mock(spec=_LogEntry, filename="/a/b/file.xml", line=23, message="A message")
    violation = Violation.from_log_entry(error)

    assert violation.filename == "file.xml"
    assert violation.line == 23
    assert violation.message == "A message"
