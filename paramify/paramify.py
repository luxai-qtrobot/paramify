import json
from ruamel.yaml import YAML
import argparse
from pydantic import BaseModel, create_model, ValidationError
from typing import Any, Dict, Type, Union


class Paramify:
    def __init__(self, config: Union[Dict[str, Any], str], enable_cli: bool = True):
        """
        A class for dynamic parameter management, validation, and runtime configuration.

        The Paramify class allows developers to define and manage parameters dynamically 
        using a configuration provided as a dictionary, JSON file, or YAML file. It also 
        provides optional command-line argument parsing and supports runtime updates with 
        automatic persistence for file-based configurations.

        Features:
        - Dynamic parameter validation using Pydantic.
        - Support for JSON and YAML configuration formats.
        - Optional CLI integration for overriding parameters at runtime.
        - Automatic persistence of parameter changes when initialized with a JSON or YAML file.
        - Custom callback methods triggered on parameter updates.

        Parameters:
        ----------
        config : Union[Dict[str, Any], str]
            A dictionary or the path to a JSON/YAML file containing the parameter configuration.
            The configuration should have a "parameters" key, which is a list of parameter definitions.

            Example Configuration:
            ```yaml
            parameters:
            - name: "param1"
                type: "bool"
                default: true
                label: "Enable Feature"
                description: "A boolean parameter to enable or disable a feature."
            - name: "param2"
                type: "int"
                default: 42
                label: "Max Value"
                description: "An integer parameter for setting the maximum value."
            ```

        enable_cli : bool, optional
            If True, enables command-line argument parsing to override parameters. Default is True.

        Raises:
        ------
        ValueError:
            If the configuration format is invalid or unsupported.
        ValidationError:
            If parameter validation fails during initialization.

        Notes:
        -----
        - When initialized with a dictionary, changes to parameters are not persisted.
        - For JSON or YAML configurations, changes are automatically saved to the file.
        - CLI changes are transient and do not persist to the file.
        """
        # Track the file path for persistence
        self._file_path = config if isinstance(config, str) else None
        self._yaml_loader = YAML()
        self._yaml_loader.preserve_quotes = True  # Retain quotes from the original file

        # Load configuration from file or dictionary
        if isinstance(config, str):
            if config.endswith('.json'):
                with open(config, 'r') as f:
                    config = json.load(f)
            elif config.endswith(('.yaml', '.yml')):
                with open(config, 'r') as f:
                    config = self._yaml_loader.load(f)
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

            # Save changes if a file path is provided
            if self._file_path:
                self._save_config()

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
                    action="store_true" # if not param.get("default", False) else "store_false"
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
                # Directly update the parameter model to avoid triggering persistence
                self.parameters.__dict__[name] = value

    def _save_config(self):
        """
        Save the current configuration back to the file with preserved formatting using ruamel.yaml.
        """
        if not self._file_path:
            return  # No file to save to

        if self._file_path.endswith(('.yaml', '.yml')):
            # Load the original YAML content to retain formatting
            with open(self._file_path, 'r') as f:
                original_data = self._yaml_loader.load(f)

            # Synchronize self.parameters with the original data
            for param in self._config_params:
                name = param['name']
                if name in self.parameters.dict():
                    for p in original_data.get('parameters', []):
                        if p['name'] == name:
                            p['default'] = self.parameters.dict()[name]

            # Save the updated configuration back to the file
            with open(self._file_path, 'w') as f:
                self._yaml_loader.dump(original_data, f)

        elif self._file_path.endswith('.json'):
            # For JSON, simply overwrite the file
            with open(self._file_path, 'w') as f:
                json.dump(self._config, f, indent=4)

    def get_parameters(self) -> Dict[str, Any]:
        """
        Return the current parameters and their values.
        """
        return self.parameters.dict()

    def __str__(self):
        """
        Return a formatted string representation of the parameters and their values.
        Includes parameter labels if available.
        """
        params = self.get_parameters()

        max_length = max(
            len(f"{p['name']} ({p.get('label', '')})") for p in self._config_params
        )  
                
        formatted_params = "\n".join(
            f"   {name} ({param.get('label', '')}){(max_length - len(name) - len(param.get('label', '')) - 2) * ' '}: {value}"
            for name, value, param in (
                (name, value, next((p for p in self._config_params if p['name'] == name), {}))
                for name, value in params.items()
            )
        )
        app_name = self._config.get('name', self.__class__.__name__)
        return f"{app_name} initialized with:\n{formatted_params}"
