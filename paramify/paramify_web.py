import os
import threading
from typing import Any, Dict, Union
from flask import Flask, jsonify, request, send_from_directory
# from flask_cors import CORS

from paramify.paramify import Paramify

class ParamifyWeb(Paramify):
    def __init__(self, config: Union[Dict[str, Any], str], host: str = '0.0.0.0', port: int = 5000):
        """
        Initialize the ParamifyWeb class, set up the Flask app, and start the server in a separate thread.
        """
        super().__init__(config)  # Initialize the parent class
        self.host = host
        self.port = port

        # Initialize Flask app with static and template folders
        base_dir = os.path.dirname(os.path.abspath(__file__))
        static_folder = os.path.join(base_dir, 'static/assets')
        template_folder = os.path.join(base_dir, 'static')

        # Initialize Flask app with static and template folders
        self.app = Flask(__name__, static_folder=static_folder, template_folder=template_folder)
        # CORS(self.app)  # Enable CORS for development convenience

        # Set up Flask routes
        self._setup_routes()

        # Start the Flask app in a separate thread
        self._start_server()

    def _setup_routes(self):
        """
        Define Flask routes for serving the Vue app and handling parameter updates.
        """

        # Serve the Vue app's index.html
        @self.app.route('/')
        @self.app.route('/<path:path>')
        def serve_frontend(path=None):
            """
            Serve static files or the Vue index.html.
            """
            if path and os.path.exists(os.path.join(self.app.template_folder, path)):
                return send_from_directory(self.app.template_folder, path)
            return send_from_directory(self.app.template_folder, 'index.html')

        # API route: Get configuration details
        @self.app.route('/api/config', methods=['GET'])
        def get_config():
            """
            Return the configuration details (metadata and current parameter values).
            """
            # Start with the original configuration metadata
            config_with_values = self._config.copy()
            
            # Update the "default" values in the parameters to reflect current values
            for param in config_with_values['parameters']:
                param_name = param['name']
                if param_name in self.get_parameters():
                    param['default'] = self.get_parameters()[param_name]
            
            return jsonify(config_with_values)
        # # API route: Get current parameter values
        # @self.app.route('/api/parameters', methods=['GET'])
        # def get_parameters():
        #     """
        #     Return the current parameter values.
        #     """
        #     return jsonify(self.get_parameters())

        # API route: Update a parameter value
        # @self.app.route('/api/parameters', methods=['POST'])
        @self.app.route('/api/update', methods=['POST'])
        def update_parameter():
            """
            Update parameters dynamically based on the received data.
            """
            data = request.json  # Example: {'param1': False, 'param2': 42}
            if not data or not isinstance(data, dict):
                return jsonify({"status": "error", "message": "Invalid request format. Expected a dictionary."}), 400

            try:
                # Iterate through the received parameters and update them
                for name, value in data.items():
                    setter = getattr(self, f"set_{name}", None)  # Dynamically find the setter
                    if not setter:
                        return jsonify({"status": "error", "message": f"Parameter '{name}' does not exist"}), 404
                    setter(value)  # Call the setter to update the parameter

                return jsonify({"status": "success", "message": "Parameters updated successfully"})
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)}), 400

    def _start_server(self):
        """
        Start the Flask app in a separate thread to avoid blocking the main thread.
        """        
        server_thread = threading.Thread(
            target=self.app.run,
            kwargs={"host": self.host, "port": self.port, "debug": False, "use_reloader": False},
            daemon=True  # Mark the thread as a daemon thread
        )
        server_thread.start()
