import unittest
from paramify.paramify import Paramify

class TestParamifyDynamicSetters(unittest.TestCase):

    def setUp(self):
        # Sample configuration for dynamic setter tests
        self.valid_dict_config = {
            "parameters": [
                {"name": "param1", "type": "bool", "default": True},
                {"name": "param2", "type": "int", "default": 42}
            ]
        }

    def test_dynamic_setter_creation(self):
        """Test that dynamic setters are created for each parameter."""
        paramify = Paramify(self.valid_dict_config, enable_cli=False)

        # Verify that setter methods exist
        self.assertTrue(hasattr(paramify, "set_param1"))
        self.assertTrue(hasattr(paramify, "set_param2"))

    def test_dynamic_setter_updates_value(self):
        """Test that dynamic setters correctly update parameter values."""
        paramify = Paramify(self.valid_dict_config, enable_cli=False)

        # Use dynamic setters to update values
        paramify.set_param1(False)
        paramify.set_param2(100)

        # Verify that values are updated
        self.assertFalse(paramify.get_parameters()["param1"])
        self.assertEqual(paramify.get_parameters()["param2"], 100)

    def test_dynamic_setter_validation(self):
        """Test that dynamic setters validate values before updating."""
        paramify = Paramify(self.valid_dict_config, enable_cli=False)

        # Attempt to set invalid values and verify exceptions
        with self.assertRaises(TypeError):
            paramify.set_param1("not_a_bool")  # Invalid bool value

        with self.assertRaises(TypeError):
            paramify.set_param2("not_an_int")  # Invalid int value

    def test_dynamic_setter_callbacks(self):
        """Test that dynamic setters invoke callback methods if defined."""
        class CallbackTestParamify(Paramify):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.callback_triggered = False

            def on_param1_set(self, value):
                self.callback_triggered = True

        # Initialize the Paramify subclass with a callback
        paramify = CallbackTestParamify(self.valid_dict_config, enable_cli=False)

        # Update param1 and verify the callback is triggered
        paramify.set_param1(False)
        self.assertTrue(paramify.callback_triggered)

if __name__ == "__main__":
    unittest.main()
