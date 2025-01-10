
# Paramify

**Paramify** is a lightweight Python library designed to simplify dynamic parameter management. It allows developers to define, validate, and manage parameters dynamically using a JSON schema, with optional support for web-based parameter configuration via Flask.

---

## Key Features

- **Dynamic Parameter Management**: Easily define and manage parameters using a simple JSON schema.
- **Validation**: Automatically validate parameters with the help of Pydantic.
- **Custom Callbacks**: Define optional callbacks to handle updates to specific parameters.
- **Web Interface**: Expose parameters through a user-friendly Flask-based UI for runtime configuration.
- **JSON Integration**: Load and manage parameters directly from JSON files for flexible configurations.
- **Extensible**: Developers can extend the base class to add custom behaviors.

---

## Installation

To install Paramify, use the following command:

```bash
pip install git+https://github.com/luxai-qtrobot/paramify.git
```

---

## Quick Start

### 1. Programmatic Parameter Management

Below is an example of using Paramify for managing parameters dynamically:

```python
from logger import Logger
from paramify.paramify import Paramify

# Define optional callback functions
class MyApp(Paramify):    
    def on_param1_set(self, value):
        Logger.info(f"param1 was updated to {value}")

    def on_param2_set(self, value):
        Logger.info(f"param2 was updated to {value}")


if __name__ == '__main__':
    params = {
        "parameters": [
            {"name": "param1", "type": "bool", "label": "Enable Feature", "default": True},
            {"name": "param2", "type": "int", "label": "Integer Value", "default": 4},
        ]
    }

    app = MyApp(params)

    # Access default or loaded values
    Logger.info(app.parameters.param1)
    Logger.info(app.parameters.param2)

    # Update values and trigger callbacks
    app.set_param1(False)
    app.set_param2(23)

    # View current parameters
    Logger.info(app.get_parameters())
```

This example demonstrates how to define parameters, set values programmatically, and trigger custom callbacks.

---

### 2. Web-Based Parameter Management

Below is an example of using **ParamifyWeb** to expose parameters through a web interface:

```python
import json
from logger import Logger
from paramify.paramify_web import ParamifyWeb

# Define optional callback functions
class MyApp(ParamifyWeb):
    def on_param1_set(self, value):
        Logger.info(f"Boolean parameter was updated to {value}")

    def on_param2_set(self, value):
        Logger.info(f"Integer parameter was updated to {value}")

    def on_param3_set(self, value):
        Logger.info(f"Float parameter was updated to {value}")

    def on_param4_set(self, value):
        Logger.info(f"Selectable parameter was updated to {value}")

    def on_param5_set(self, value):
        Logger.info(f"List parameter was updated to {value}")

    def on_param6_set(self, value):
        Logger.info(f"Simple string was updated to {value}")

    def on_param7_set(self, value):
        Logger.info(f"Text area value was updated to {value}")


if __name__ == '__main__':
    # Load parameters from a JSON file
    try:
        with open('config.json', "r") as f:
            params = json.load(f)
            Logger.info("Parameters loaded from config.json")
    except Exception as e:
        Logger.error(f"Failed to load parameters from JSON file: {e}")

    # Initialize the app with parameters
    app = MyApp(params)

    # Prevent the script from exiting immediately
    input("Press Enter to continue...")
```

This example demonstrates how to load parameters from a JSON file and expose them via a Flask web interface. Callback functions are triggered when parameters are updated.

---

## JSON Configuration Example

Here is an example of a JSON configuration file:

```json
{
    "name": "My Example App",
    "description": "This is an example app to demonstrate the usage of ParamifyWeb",
    "parameters": [
        {
            "name": "param1",
            "type": "bool",
            "label": "Enable Feature",
            "description": "A boolean parameter to enable or disable a feature.",
            "default": true
        },
        {
            "name": "param2",
            "type": "int",
            "label": "Integer Value",
            "description": "An integer parameter for numeric configuration.",
            "default": 4,
            "ui": {"element": "slider", "min": 1, "max": 10}
        },
        {
            "name": "param3",
            "type": "float",
            "label": "Floating Point Value",
            "description": "A float parameter for precision configuration.",
            "default": 7.5
        },
        {
            "name": "param4",
            "type": "str",
            "label": "Select Option",
            "description": "A parameter to select from predefined options.",
            "default": "option 2",
            "ui": {"element": "select", "items": ["option 1", "option 2", "option 3"]}
        }
    ]
}
```

---

## Features Overview

- **Ease of Use**: Simple, human-readable JSON schema for parameter definitions.
- **Web UI**: Manage and modify parameters in real-time through a web interface.
- **Custom Logic**: Implement application-specific callbacks for parameters.
- **JSON Support**: Load configurations from external JSON files for flexibility.

---

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to improve this library.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

