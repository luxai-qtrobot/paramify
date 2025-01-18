import unittest
from paramify.paramify import Paramify
from tempfile import NamedTemporaryFile

class TestParamifyValidation(unittest.TestCase):

    def setUp(self):
        # Prepare sample configurations for testing
        self.valid_dict_config = {
            "parameters": [
                {"name": "param1", "type": "bool", "default": True},
                {"name": "param2", "type": "int", "default": 42}
            ]
        }

    def tearDown(self):
        pass

    def test_valid_dict_configuration(self):
        """Test initialization with a valid dictionary configuration."""
        paramify = Paramify(self.valid_dict_config, enable_cli=False)  # Disable CLI parsing
        self.assertEqual(paramify.get_parameters()["param1"], True)
        self.assertEqual(paramify.get_parameters()["param2"], 42)

    def test_type_enforcement(self):
        """Test that parameter types are enforced during initialization."""
        invalid_config = {
            "parameters": [
                {"name": "param1", "type": "bool", "default": "not_a_bool"},  # Invalid bool
                {"name": "param2", "type": "int", "default": "not_an_int"}   # Invalid int
            ]
        }

        with self.assertRaises(ValueError):
            Paramify(invalid_config, enable_cli=False)

    def test_missing_default(self):
        """Test that parameters without a default are initialized as None."""
        config = {
            "parameters": [
                {"name": "param1", "type": "str"},  # No default value
                {"name": "param2", "type": "int", "default": 10}
            ]
        }
        paramify = Paramify(config, enable_cli=False)
        self.assertIsNone(paramify.get_parameters()["param1"])
        self.assertEqual(paramify.get_parameters()["param2"], 10)


    def test_optional_parameters(self):
        """Test that parameters without default values are treated as optional."""
        config = {
            "parameters": [
                {"name": "param1", "type": "float"}  # No default
            ]
        }
        paramify = Paramify(config, enable_cli=False)
        self.assertIsNone(paramify.get_parameters()["param1"])

if __name__ == "__main__":
    unittest.main()
