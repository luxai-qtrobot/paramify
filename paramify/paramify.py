import json
import yaml
import argparse
from pydantic import BaseModel, create_model, ValidationError
from typing import Any, Dict, Type, Union


class Paramify:
    def __init__(self, config: Union[Dict[str, Any], str], enable_cli: bool = True):
        """
        Initialize Paramify with a dictionary, a JSON file, or a YAML file.
        Optionally parse command-line arguments if enable_cli is True.
        """
        # Load configuration from file or dictionary
        if isinstance(config, str):
            if config.endswith('.json'):
                with open(config, 'r') as f:
                    config = json.load(f)
            elif config.endswith(('.yaml', '.yml')):
                with open(config, 'r') as f:
                    config = yaml.safe_load(f)
            else:
                raise ValueError("Unsupported file format. Use a JSON or YAML file.")
        elif not isinstance(config, dict):
            raise ValueError("Config must be a dictionary or a valid JSON/YAML file path.")

        self._config = config

        if not isinstance(config, dict) or 'parameters' not in config:
            raise ValueError("Invalid configuration format. Expected a 'parameters' key.")

        self._config_params: list = config['parameters']

        # Dynamically create a Pydantic model
        self.ParameterModel = self._create_model(self._config_params)
        try:
            self.parameters = self.ParameterModel(**{p['name']: p.get('default', None) for p in self._config_params})
        except ValidationError as e:
            print("Validation Error in Configuration:", e)
            raise

        # Parse CLI arguments if enabled
        if enable_cli:
            self._parse_cli_args()

        # Dynamically create setters for each parameter
        for param in self._config_params:
            self._add_parameter(param['name'])

    def _create_model(self, config_data: list) -> Type[BaseModel]:
        """
        Dynamically create a Pydantic BaseModel based on the configuration data.
        Fields without a default value or explicitly set to `None` are marked as optional.
        """
        from typing import Optional

        fields = {}
        for param in config_data:
            field_type = eval(param['type'])  # Determine the type
            default = param.get('default', None)  # Get the default value, or None if not provided

            if default is None:
                # If no default value is provided, make the field optional
                fields[param['name']] = (Optional[field_type], default)
            else:
                # Otherwise, set the field type and default value
                fields[param['name']] = (field_type, default)

        return create_model('ParameterModel', **fields)

    def _add_parameter(self, name: str):
        """
        Dynamically create a setter method with validation and a callback for each parameter.
        """
        def setter(self, value: Any):
            # Validate the updated value by creating a new validated model
            try:
                updated_params = self.parameters.dict()  # Get current parameters as a dictionary
                updated_params[name] = value             # Update the parameter
                self.parameters = self.ParameterModel(**updated_params)  # Revalidate
            except ValidationError as e:
                raise TypeError(f"Invalid value for {name}: {e}")

            # Invoke the callback for the parameter if defined
            callback_name = f"on_{name}_set"
            if hasattr(self, callback_name) and callable(getattr(self, callback_name)):
                getattr(self, callback_name)(value)

        # Attach the setter method to the class
        setattr(self, f"set_{name}", setter.__get__(self))

    def _parse_cli_args(self):
        """
        Parse CLI arguments and update the parameters accordingly.
        """
        self.parser = argparse.ArgumentParser(description=self._config.get("description", ""))

        for param in self._config_params:
            scope = param.get("scope", "all")
            if scope not in ["all", "cli"]:
                continue  # Only include parameters with scope "all" or "cli" in the CLI

            arg_name = f"--{param['name'].replace('_', '-')}"
            param_type = param["type"]

            if param_type == "bool":
                # Use `store_true` or `store_false` for boolean arguments
                self.parser.add_argument(
                    arg_name,
                    help=param.get("description", ""),
                    default=param.get("default", False),
                    action="store_true" if not param.get("default", False) else "store_false"
                )
            elif param_type == "list":
                # Handle list arguments with nargs="+"
                self.parser.add_argument(
                    arg_name,
                    help=param.get("description", ""),
                    nargs="+",
                    default=param.get("default", []),
                    type=str  # Assume lists are of type str; adjust as needed
                )
            else:
                # Add other parameter types
                self.parser.add_argument(
                    arg_name,
                    help=param.get("description", ""),
                    default=param.get("default"),
                    type=eval(param_type) if param_type in ["int", "float", "str"] else str
                )

        # Parse arguments and update parameters
        args = self.parser.parse_args()
        cli_args = vars(args)
        for name, value in cli_args.items():
            if name in self.parameters.dict():
                setattr(self.parameters, name, value)

    def get_parameters(self) -> Dict[str, Any]:
        """
        Return the current parameters and their values.
        """
        return self.parameters.dict()
