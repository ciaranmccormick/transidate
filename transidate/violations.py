import re
from dataclasses import dataclass


@dataclass
class Violation:
    element: str
    details: str


class ViolationProcessor:
    namespace_regex = re.compile(r"(\{.*?\})")
    element_regex = re.compile(r"^Element '([A-Za-z]*)':")
    details_regex = re.compile(r"^.*: (.*)$")

    def process(self, text):
        text = self._strip_namespace(text)
        name = self._get_element_name(text)
        details = self._get_details(text)
        return Violation(element=name, details=details)

    def _strip_namespace(self, text):
        """Removes namespaces from XML error messages."""
        replacement = self.namespace_regex.sub("", text)
        return replacement

    def _get_element_name(self, text):
        """Extracts the offending element from a lxml error message."""
        match = self.element_regex.match(text)
        if match:
            return match.group(1)
        return ""

    def _get_details(self, text):
        """Extracts the error details from an lxml error message."""
        match = self.details_regex.match(text)
        if match:
            return match.group(1)
        return ""
