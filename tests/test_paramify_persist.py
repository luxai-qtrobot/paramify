import unittest
import json
import os
from tempfile import NamedTemporaryFile
from paramify.paramify import Paramify
from ruamel.yaml import YAML

class TestParamifyPersistence(unittest.TestCase):

    def setUp(self):
        # Prepare a valid JSON configuration file
        self.valid_json_config = {
            "parameters": [
                {"name": "param1", "type": "bool", "default": True},
                {"name": "param2", "type": "int", "default": 42}
            ]
        }

        self.valid_json_file = NamedTemporaryFile(suffix=".json", mode="w", delete=False)
        json.dump(self.valid_json_config, self.valid_json_file)
        self.valid_json_file.close()

        # Prepare a valid YAML configuration file
        self.valid_yaml_file = NamedTemporaryFile(suffix=".yaml", mode="w", delete=False)
        yaml = YAML()
        yaml.dump(self.valid_json_config, self.valid_yaml_file)
        self.valid_yaml_file.close()

    def tearDown(self):
        # Clean up temporary files
        os.unlink(self.valid_json_file.name)
        os.unlink(self.valid_yaml_file.name)

    def test_json_persistence(self):
        """Test that changes to parameters are persisted to a JSON file."""
        paramify = Paramify(self.valid_json_file.name, enable_cli=False)

        # Update parameters
        paramify.set_param1(False)
        paramify.set_param2(100)

        # Reload the file and verify changes
        with open(self.valid_json_file.name, "r") as f:
            updated_config = json.load(f)

        updated_params = {p["name"]: p["default"] for p in updated_config["parameters"]}
        self.assertFalse(updated_params["param1"])
        self.assertEqual(updated_params["param2"], 100)

    def test_yaml_persistence(self):
        """Test that changes to parameters are persisted to a YAML file."""
        paramify = Paramify(self.valid_yaml_file.name, enable_cli=False)

        # Update parameters
        paramify.set_param1(False)
        paramify.set_param2(100)

        # Reload the file and verify changes
        yaml = YAML()
        with open(self.valid_yaml_file.name, "r") as f:
            updated_config = yaml.load(f)

        updated_params = {p["name"]: p["default"] for p in updated_config["parameters"]}
        self.assertFalse(updated_params["param1"])
        self.assertEqual(updated_params["param2"], 100)

    def test_no_persistence_for_dict_config(self):
        """Test that changes are not persisted when initialized with a dictionary configuration."""
        paramify = Paramify(self.valid_json_config, enable_cli=False)

        # Update parameters
        paramify.set_param1(False)
        paramify.set_param2(100)

        # Verify the original configuration is unchanged
        self.assertTrue(self.valid_json_config["parameters"][0]["default"])
        self.assertEqual(self.valid_json_config["parameters"][1]["default"], 42)

if __name__ == "__main__":
    unittest.main()
