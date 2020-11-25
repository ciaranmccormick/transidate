from transidate.violations import Violation, ViolationProcessor


class TestViolationProcessor:
    message = (
        "Element '{http://www.transxchange.org.uk/}Latitude': 'Hello,World' "
        "is not a valid value of the atomic type '{http://www.transxchange.org.uk/}"
        "LatitudeType'."
    )

    def test_extract_element_from_message(self):
        processor = ViolationProcessor()
        cleaned = processor._strip_namespace(self.message)
        actual = processor._get_element_name(cleaned)
        expected = "Latitude"
        assert expected == actual

        expected = ""
        test_input = "blahblahblah"
        actual = processor._get_element_name(test_input)
        assert expected == actual

    def test_strip_namespace(self):
        processor = ViolationProcessor()
        cleaned = processor._strip_namespace(self.message)
        actual = processor._get_details(cleaned)
        expected = (
            "'Hello,World' is not a valid value of the atomic type 'LatitudeType'."
        )
        assert expected == actual

        expected = ""
        test_input = "blahblahblah"
        actual = processor._get_details(test_input)
        assert expected == actual

    def test_clean_message(self):
        processor = ViolationProcessor()
        actual = processor.process(self.message)
        expected = Violation(
            "Latitude",
            "'Hello,World' is not a valid value of the atomic type 'LatitudeType'.",
        )
        assert expected == actual
