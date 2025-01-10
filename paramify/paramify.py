import json
import yaml
from pydantic import BaseModel, create_model, ValidationError
from typing import Any, Dict, Type, Union

class Paramify:
    def __init__(self, config: Union[Dict[str, Any], str]):
        """
        Initialize the class by dynamically generating a Pydantic model
        and creating setters for each parameter.
        """

        """
        Initialize Paramify with a dictionary, a JSON file, or a YAML file.
        """
        if isinstance(config, str):  # If a string, assume it's a file path
            if config.endswith('.json'):  # JSON file
                with open(config, 'r') as f:
                    config = json.load(f)
            elif config.endswith(('.yaml', '.yml')):  # YAML file
                with open(config, 'r') as f:
                    config = yaml.safe_load(f)
            else:
                raise ValueError("Unsupported file format. Use a JSON or YAML file.")
        elif not isinstance(config, dict):  # Validate input
            raise ValueError("Config must be a dictionary or a valid JSON/YAML file path.")

        self._config = config        
        

        if not isinstance(config, dict) or 'parameters' not in config:
            raise ValueError("Invalid configuration format. Expected a 'parameters' key.")
        
        self._config_params:list = config['parameters']

        # Dynamically create a Pydantic model
        self.ParameterModel = self._create_model(self._config_params)
        try:
            self.parameters = self.ParameterModel(**{p['name']: p['default'] for p in self._config_params})
        except ValidationError as e:
            print("Validation Error in Configuration:", e)
            raise

        # Dynamically create setters for each parameter
        for param in self._config_params:
            self._add_parameter(param['name'])

    def _create_model(self, config_data: list) -> Type[BaseModel]:
        """
        Dynamically create a Pydantic BaseModel based on the configuration data.
        """
        fields = {
            param['name']: (eval(param['type']), param.get('default', None))
            for param in config_data
        }
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

    def get_parameters(self) -> Dict[str, Any]:
        """
        Return the current parameters and their values.
        """
        return self.parameters.dict()
