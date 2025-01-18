import unittest
from paramify.paramify import Paramify

class TestParamifyPerformanceEdgeCases(unittest.TestCase):

    def setUp(self):
        # Sample configuration for edge case and performance testing
        self.small_config = {
            "parameters": [
                {"name": "param1", "type": "bool", "default": True, "label": "Enable Feature"},
                {"name": "param2", "type": "int", "default": 42, "label": "Maximum Value"}
            ],
            "name": "TestApp"
        }

        self.large_config = {
            "parameters": [
                {"name": f"param{i}", "type": "int", "default": i} for i in range(1000)
            ],
            "name": "LargeTestApp"
        }

    def test_large_configuration(self):
        """Test initialization and operations with a large configuration."""
        paramify = Paramify(self.large_config, enable_cli=False)

        # Verify that all parameters are initialized correctly
        parameters = paramify.get_parameters()
        self.assertEqual(len(parameters), 1000)
        for i in range(1000):
            self.assertEqual(parameters[f"param{i}"], i)

    def test_edge_case_parameter_names(self):
        """Test handling of edge case parameter names."""
        edge_case_config = {
            "parameters": [
                {"name": "param_with_@_symbol", "type": "str", "default": "value"},
                {"name": "param_with_a_really_really_long_name_exceeding_normal_limits", "type": "int", "default": 999},
                {"name": "param_with spaces", "type": "bool", "default": True}
            ]
        }

        paramify = Paramify(edge_case_config, enable_cli=False)
        parameters = paramify.get_parameters()

        # Verify that all edge case parameters are handled correctly
        self.assertEqual(parameters["param_with_@_symbol"], "value")
        self.assertEqual(parameters["param_with_a_really_really_long_name_exceeding_normal_limits"], 999)
        self.assertTrue(parameters["param_with spaces"])

    def test_empty_configuration(self):
        """Test initialization with an empty configuration."""
        with self.assertRaises(ValueError):
            Paramify({}, enable_cli=False)

    def test_conflicting_updates(self):
        """Test behavior when conflicting updates are made via setters and CLI arguments."""
        class ConflictParamify(Paramify):
            def on_param2_set(self, value):
                self.param2_updated_via_setter = value

        config = {
            "parameters": [
                {"name": "param1", "type": "bool", "default": True},
                {"name": "param2", "type": "int", "default": 42}
            ]
        }

        # Simulate CLI arguments
        with unittest.mock.patch('sys.argv', ['execution.py', '--param2', '100']):
            paramify = ConflictParamify(config, enable_cli=True)

        # Update via setter after CLI parsing
        paramify.set_param2(200)

        # Verify the final value
        self.assertEqual(paramify.get_parameters()["param2"], 200)
        self.assertEqual(paramify.param2_updated_via_setter, 200)

    def test_stress_dynamic_updates(self):
        """Stress test for dynamically updating a large number of parameters."""
        paramify = Paramify(self.large_config, enable_cli=False)

        # Dynamically update all parameters
        for i in range(1000):
            setter = getattr(paramify, f"set_param{i}")
            setter(i * 2)  # Double each parameter's value

        # Verify the updates
        parameters = paramify.get_parameters()
        for i in range(1000):
            self.assertEqual(parameters[f"param{i}"], i * 2)

if __name__ == "__main__":
    unittest.main()
