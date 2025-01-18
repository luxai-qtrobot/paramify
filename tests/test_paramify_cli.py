import unittest
from paramify.paramify import Paramify
import sys
from unittest.mock import patch
from io import StringIO

class TestParamifyCLI(unittest.TestCase):

    def setUp(self):
        # Prepare sample configurations for CLI testing
        self.valid_dict_config = {
            "parameters": [
                {"name": "param1", "type": "bool", "default": True},
                {"name": "param2", "type": "int", "default": 42}
            ]
        }

    @patch.object(sys, 'argv', ['execution.py', '--param1', '--param2', '100'])
    def test_override_parameters_via_cli(self):
        """Test that CLI arguments correctly override parameter values."""
        paramify = Paramify(self.valid_dict_config, enable_cli=True)
        self.assertTrue(paramify.get_parameters()["param1"])
        self.assertEqual(paramify.get_parameters()["param2"], 100)

    @patch.object(sys, 'argv', ['execution.py', '--param2', 'not_an_int'])
    def test_invalid_cli_overrides(self):
        """Test that invalid CLI input is handled gracefully."""
        # Redirect stderr to capture argparse's error output
        stderr = StringIO()
        with patch('sys.stderr', stderr), self.assertRaises(SystemExit) as context:
            Paramify(self.valid_dict_config, enable_cli=True)
        
        # Capture the error message and check its content
        error_message = stderr.getvalue()
        self.assertIn("argument --param2: invalid int value: 'not_an_int'", error_message)
        self.assertIn("usage:", error_message)  # Ensure the usage message is included


    @patch.object(sys, 'argv', ['execution.py', '--param1', '--param2', '42'])
    def test_partial_cli_override(self):
        """Test that CLI arguments can partially override default values."""
        paramify = Paramify(self.valid_dict_config, enable_cli=True)
        self.assertTrue(paramify.get_parameters()["param1"])
        self.assertEqual(paramify.get_parameters()["param2"], 42)

if __name__ == "__main__":
    unittest.main()
