from transidate.validators import Validators


def test_txc21_validation(txc21_archive):
    validator = Validators.get_validator("TXC2.1")
    result = validator.validate(txc21_archive)
    assert result.status == result.OK
    assert len(result.violations) == 0


def test_txc24_validation(txc24_archive):
    validator = Validators.get_validator("TXC2.4")
    result = validator.validate(txc24_archive)
    assert result.status == result.OK
    assert len(result.violations) == 0
