from pathlib import Path
from typing import Optional
from unittest.mock import Mock, patch

import pytest

from transidate.exceptions import NotRegistered, NotSupported
from transidate.validators import (
    ValidationResult,
    Validator,
    ValidatorFactory,
    Validators,
)


class ValidatorTest:
    _validator: Optional[Validator] = None
    version = ""

    @property
    def validator(self):
        if self._validator:
            return self._validator

        self._validator = Validators.get_validator(self.version)
        return self._validator


class TestTransXChange21Document(ValidatorTest):
    version = "TXC2.1"

    def test_validate(self, txc21):
        result = self.validator.validate(txc21)
        expected = ValidationResult(
            status=ValidationResult.OK,
            violations=[],
        )
        assert expected == result


class TestTransXChange24Document(ValidatorTest):
    version = "TXC2.4"

    def test_validate(self, txc24):
        result = self.validator.validate(txc24)
        expected = ValidationResult(
            status=ValidationResult.OK,
            violations=[],
        )
        assert expected == result

    def test_validate_malformed_file(self, txc24invalid):
        result = self.validator.validate(txc24invalid)
        assert result.ERROR == result.status
        assert len(result.violations) == 2


class TestNeTExValidator:
    def test_validate(self, netex):
        validator = Validators.get_validator("NTXPUB1.10")
        result = validator.validate(netex)
        assert result.OK == result.status
        assert len(result.violations) == 0


class TestSiriValidator:
    def test_validate(self, siri2):
        validator = Validators.get_validator("SIRI2.0")
        result = validator.validate(siri2)
        assert result.OK == result.status
        assert len(result.violations) == 0


def test_validator_factory_registered_schemas():
    factory = ValidatorFactory()  # type: ignore
    factory.register_schema("KEY1", url="https://afakeurl.url", root_path="root.xsd")
    assert list(factory.registered_schemas) == ["KEY1"]


def test_unregistered_validator():
    factory = ValidatorFactory()  # type: ignore
    factory.register_schema("KEY1", url="https://afakeurl.url", root_path="root.xsd")
    with pytest.raises(NotRegistered) as exc:
        factory.get_validator("KEY2")
    assert str(exc.value) == "Schema 'KEY2' was not registered."


@patch("transidate.validators.etree.parse", side_effect=OSError)
def test_get_xsd(mparse):
    validator = Validator(url="https://afakeurl.url", root_path="root.xsd")
    path = Mock(spec=Path)
    path.glob.return_value = [Mock(), Mock()]
    with pytest.raises(NotSupported) as exc:
        validator.get_xsd(path)

    assert str(exc.value) == "Source 'root.xsd' cannot be parsed."
