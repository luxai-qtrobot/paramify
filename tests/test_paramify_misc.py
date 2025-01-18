import unittest
from paramify.paramify import Paramify

class TestParamifyMiscellaneous(unittest.TestCase):

    def setUp(self):
        # Sample configuration for testing miscellaneous methods
        self.valid_dict_config = {
            "parameters": [
                {"name": "param1", "type": "bool", "default": True, "label": "Enable Feature"},
                {"name": "param2", "type": "int", "default": 42, "label": "Maximum Value"}
            ],
            "name": "TestApp"
        }

    def test_get_parameters(self):
        """Test that get_parameters returns the current parameter values as a dictionary."""
        paramify = Paramify(self.valid_dict_config, enable_cli=False)
        parameters = paramify.get_parameters()

        # Verify the returned dictionary matches the expected values
        expected_parameters = {
            "param1": True,
            "param2": 42
        }
        self.assertEqual(parameters, expected_parameters)

    def test_update_non_existent_parameter(self):
        """Test that updating a non-existent parameter raises an AttributeError."""
        paramify = Paramify(self.valid_dict_config, enable_cli=False)

        # Attempt to set a parameter that doesn't exist
        with self.assertRaises(AttributeError):
            paramify.set_param3("value")  # param3 is not defined

    def test_invalid_type_update(self):
        """Test that updating a parameter with an invalid type raises TypeError."""
        paramify = Paramify(self.valid_dict_config, enable_cli=False)

        # Attempt to set an invalid type
        with self.assertRaises(TypeError):
            paramify.set_param1("not_a_bool")  # param1 expects a bool

        with self.assertRaises(TypeError):
            paramify.set_param2("not_an_int")  # param2 expects an int

    def test_out_of_range_update(self):
        """Test that updating a parameter with a value out of acceptable range raises an error."""
        class RangeValidatingParamify(Paramify):
            def on_param2_set(self, value):
                if not (0 <= value <= 100):
                    raise ValueError("param2 must be between 0 and 100")

        paramify = RangeValidatingParamify(self.valid_dict_config, enable_cli=False)

        # Attempt to set a value out of range
        with self.assertRaises(ValueError):
            paramify.set_param2(150)  # Out of range for param2
                        
if __name__ == "__main__":
    unittest.main()
