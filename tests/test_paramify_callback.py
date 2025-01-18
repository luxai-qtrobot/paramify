import unittest
from paramify.paramify import Paramify

class TestParamifyCallbacks(unittest.TestCase):

    def setUp(self):
        # Sample configuration with basic parameters
        self.valid_dict_config = {
            "parameters": [
                {"name": "param1", "type": "bool", "default": True},
                {"name": "param2", "type": "int", "default": 42}
            ]
        }

    def test_callback_invocation(self):
        """Test that the appropriate callback is invoked when a parameter is updated."""
        class CallbackTestParamify(Paramify):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.callback_invoked = False

            def on_param1_set(self, value):
                self.callback_invoked = True

        # Instantiate the custom Paramify class
        paramify = CallbackTestParamify(self.valid_dict_config, enable_cli=False)

        # Update param1 and verify the callback was invoked
        paramify.set_param1(False)
        self.assertTrue(paramify.callback_invoked)

    def test_no_callback(self):
        """Test that no error occurs when no callback is defined for a parameter."""
        paramify = Paramify(self.valid_dict_config, enable_cli=False)

        # Update param2, which has no callback, and verify no exceptions are raised
        try:
            paramify.set_param2(100)
        except Exception as e:
            self.fail(f"Unexpected exception raised: {e}")

    def test_callback_with_correct_value(self):
        """Test that the callback receives the correct updated value."""
        class ValueCallbackTestParamify(Paramify):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.callback_value = None

            def on_param2_set(self, value):
                self.callback_value = value

        # Instantiate the custom Paramify class
        paramify = ValueCallbackTestParamify(self.valid_dict_config, enable_cli=False)

        # Update param2 and verify the callback received the correct value
        paramify.set_param2(100)
        self.assertEqual(paramify.callback_value, 100)

if __name__ == "__main__":
    unittest.main()
