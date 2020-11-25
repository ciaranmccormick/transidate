from pathlib import Path
from unittest.mock import Mock, patch

from transidate import ValidationResult
from transidate.validators import (
    NeTExValidator,
    SiriValidator,
    TransXChangeValidator,
    ValidationError,
    XMLValidator,
)
from transidate.violations import Violation


class TestXMLValidator:
    @patch("transidate.validators.etree")
    def test_filename(self, metree):
        has_filename = Mock(filename="filename")
        validator = XMLValidator(has_filename)
        assert validator.filename == "filename"
        metree.parse.assert_called_once()

    @patch("transidate.validators.etree")
    def test_no_filename(self, metree):
        name = "filename"
        validator = XMLValidator(name)
        assert validator.filename == name
        metree.parse.assert_called_once()


class TestTransXChange21Document:
    def test_get_document_type(self, txc21):
        validator = TransXChangeValidator(txc21)
        expected = "TransXChange"
        assert expected == validator.name

    def test_get_document_version(self, txc21):
        validator = TransXChangeValidator(txc21)
        expected = "2.1"
        assert expected == validator.version

    def test_validate(self, txc21):
        validator = TransXChangeValidator(txc21)
        expected = ValidationResult(
            status=ValidationResult.OK,
            errors=[],
            filename=validator.filename,
            version=validator.version,
            data_type="TransXChange",
        )
        actual = validator.validate()
        assert expected == actual


class TestTransXChange24Document:
    def test_get_document_type(self, txc24):
        validator = TransXChangeValidator(txc24)
        expected = "TransXChange"
        assert expected == validator.name

    def test_get_document_version(self, txc24):
        validator = TransXChangeValidator(txc24)
        expected = "2.4"
        assert expected == validator.version

    def test_validate(self, txc24):
        validator = TransXChangeValidator(txc24)
        expected = ValidationResult(
            status=ValidationResult.OK,
            errors=[],
            filename=validator.filename,
            version=validator.version,
            data_type=validator.name,
        )
        actual = validator.validate()
        assert expected == actual

    def test_validate_malformed_file(self, txc24invalid):
        validator = TransXChangeValidator(txc24invalid)
        actual = validator.validate()
        expected_errors = [
            ValidationError(
                filename=Path(validator.filename).name,
                line=32,
                type_name="SCHEMAV_CVC_DATATYPE_VALID_1_2_1",
                message=Violation(
                    "Latitude",
                    "'blah' is not a valid value of the atomic type 'LatitudeType'.",
                ),
            ),
            ValidationError(
                filename=Path(validator.filename).name,
                line=120,
                type_name="SCHEMAV_CVC_DATATYPE_VALID_1_2_1",
                message=Violation(
                    "Latitude",
                    "'Hello,World' is not a valid value of the atomic type 'LatitudeType'.",
                ),
            ),
        ]

        expected = ValidationResult(
            status=ValidationResult.ERROR,
            errors=expected_errors,
            filename=validator.filename,
            version=validator.version,
            data_type=validator.name,
        )
        assert expected == actual


class TestNeTExValidator:
    def test_create_validator(self, netex):
        validator = NeTExValidator(netex)
        assert validator.version == "1.0"
        assert validator.name == "NeTEx"

    def test_validate(self, netex):
        validator = NeTExValidator(netex)
        actual = validator.validate()
        expected = ValidationResult(
            status=ValidationResult.OK,
            filename=validator.filename,
            version=validator.version,
            data_type=validator.name,
            errors=[],
        )
        assert actual == expected


class TestSiriValidator:
    def test_create_validator(self, siri2):
        validator = SiriValidator(siri2)
        assert validator.version == "2.0"
        assert validator.name == "Siri"

    def test_validate(self, siri2):
        validator = SiriValidator(siri2)
        actual = validator.validate()
        expected = ValidationResult(
            status=ValidationResult.OK,
            filename=validator.filename,
            version=validator.version,
            data_type=validator.name,
            errors=[],
        )
        assert actual == expected
