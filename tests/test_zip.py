from transidate.zip import ZipValidator


class TestTransXChangeZip:
    def test_validate_files(self, txc24_zip):
        validator = ZipValidator(txc24_zip)
        results = [result for result in validator.validate_files()]
        actual = [result.errors for result in results]
        expected = [[], [], []]
        assert expected == actual
        assert len(validator._schemas) == 1
