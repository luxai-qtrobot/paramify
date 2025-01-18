import unittest
import json
import os
from paramify.paramify import Paramify
from tempfile import NamedTemporaryFile
from ruamel.yaml import scanner


class TestParamifyInitialization(unittest.TestCase):

    def setUp(self):
        # Prepare sample configurations for testing
        self.valid_dict_config = {
            "parameters": [
                {"name": "param1", "type": "bool", "default": True},
                {"name": "param2", "type": "int", "default": 42}
            ]
        }

        self.valid_json_file = NamedTemporaryFile(suffix=".json", mode='w', delete=False)
        json.dump(self.valid_dict_config, self.valid_json_file)
        self.valid_json_file.close()

        self.invalid_json_file = NamedTemporaryFile(suffix=".json", mode='w', delete=False)
        self.invalid_json_file.write("invalid-json")
        self.invalid_json_file.close()

        self.valid_yaml_file = NamedTemporaryFile(suffix=".yaml", mode='w', delete=False)
        self.valid_yaml_file.write("parameters:\n  - name: param1\n    type: bool\n    default: true\n  - name: param2\n    type: int\n    default: 42\n")
        self.valid_yaml_file.close()

        self.invalid_yaml_file = NamedTemporaryFile(suffix=".yaml", mode='w', delete=False)
        self.invalid_yaml_file.write("invalid: yaml: content")
        self.invalid_yaml_file.close()

    def tearDown(self):
        # Clean up temporary files
        os.unlink(self.valid_json_file.name)
        os.unlink(self.invalid_json_file.name)
        os.unlink(self.valid_yaml_file.name)
        os.unlink(self.invalid_yaml_file.name)

    def test_valid_dict_configuration(self):
        """Test initialization with a valid dictionary configuration."""
        paramify = Paramify(self.valid_dict_config, enable_cli=False)
        self.assertEqual(paramify.get_parameters()["param1"], True)
        self.assertEqual(paramify.get_parameters()["param2"], 42)

    def test_valid_json_file_configuration(self):
        """Test initialization with a valid JSON file."""
        paramify = Paramify(self.valid_json_file.name, enable_cli=False)
        self.assertEqual(paramify.get_parameters()["param1"], True)
        self.assertEqual(paramify.get_parameters()["param2"], 42)

    def test_valid_yaml_file_configuration(self):
        """Test initialization with a valid YAML file."""
        paramify = Paramify(self.valid_yaml_file.name, enable_cli=False)
        self.assertEqual(paramify.get_parameters()["param1"], True)
        self.assertEqual(paramify.get_parameters()["param2"], 42)

    def test_invalid_file_format(self):
        """Test that an invalid file format raises a ValueError."""
        with self.assertRaises(ValueError):
            Paramify("invalid_file.txt")

    def test_invalid_json_configuration(self):
        """Test that an invalid JSON file raises a ValueError."""
        with self.assertRaises(ValueError):
            Paramify(self.invalid_json_file.name)

    def test_invalid_yaml_configuration(self):
        """Test that an invalid YAML file raises a ValueError."""
        with self.assertRaises(scanner.ScannerError):
            Paramify(self.invalid_yaml_file.name, enable_cli=False)

    def test_missing_parameters_key(self):
        """Test that a configuration without a 'parameters' key raises a ValueError."""
        invalid_config = {"settings": []}  # Missing 'parameters' key
        with self.assertRaises(ValueError):
            Paramify(invalid_config)

    def test_empty_configuration(self):
        """Test that an empty configuration raises a ValueError."""
        with self.assertRaises(ValueError):
            Paramify({})

if __name__ == "__main__":
    unittest.main()
