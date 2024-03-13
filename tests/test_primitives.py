import unittest
from src.pymaze.view.primitives import tag


class TagTestCases(unittest.TestCase):
    def test_element_name(self):
        """should return self-closing element name"""
        actual = tag("svg")
        expected = "<svg />"
        self.assertEqual(expected, actual)

    def test_element_name_and_value(self):
        """should return self-closing element name and value"""
        actual = tag("svg", "Your web browser doesn't support SVG")
        expected = "<svg>Your web browser doesn't support SVG</svg>"
        self.assertEqual(expected, actual)

    def test_element_name_and_attributes(self):
        """should return self-closing element name and attributes (including one with a hyphen)"""
        actual = tag("svg", xmlns="http://www.w3.org/2000/svg", stroke_linejoin="round")
        expected = '<svg xmlns="http://www.w3.org/2000/svg" stroke-linejoin="round" />'
        self.assertEqual(expected, actual)

    def test_element_name_value_and_attributes(self):
        """should return element name and attributes and value"""
        actual = tag("svg", "SVG not supported", width="100%", height="100%")
        expected = '<svg width="100%" height="100%">SVG not supported</svg>'
        self.assertEqual(expected, actual)

    def test_nested_elements(self):
        """should return nested elements with attributes """
        actual = tag("svg", tag("rect", fill="blue"), width="100%")
        expected = '<svg width="100%"><rect fill="blue" /></svg>'
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
