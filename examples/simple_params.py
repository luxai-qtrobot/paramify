from logger import Logger
from paramify.paramify import Paramify

# define optional call back functions to be triggered when a parameter is updated
class MyApp(Paramify):    
    def on_param1_set(self, value):
        Logger.info(f"param1 was updated to {value}")

    def on_param2_set(self, value):
        Logger.info(f"param2 was updated to {value}")


if __name__ == '__main__':
    params = {
        "parameters": [
            {"name": "param1", "type": "bool", "label": "Parameter 1", "default": False, "description": "This is a boolean parameter"},
            {"name": "param2", "type": "int", "label": "Parameter 2", "default": 4, "description": "This is an integer parameter"},
        ]
    }

    app = MyApp(params)

    # Access default or loaded values
    Logger.info(app.parameters.param1)
    Logger.info(app.parameters.param2)

    # # Update values and trigger callbacks
    app.set_param1(False)
    app.set_param2(23)

    # View current parameters
    Logger.info(app.get_parameters())

    