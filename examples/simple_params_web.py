import json
from logger import Logger
from paramify.paramify_web import ParamifyWeb


# Define optional callback functions to be triggered when a parameter is updated
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
    # load parameters from a JSON file
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
