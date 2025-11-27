import logging
from flask import Flask
from threading import Thread
from route import web_routes  # Import the routes we defined in route.py

# Initialize Flask App
web_app = Flask(__name__)

# Register the routes from route.py
web_app.register_blueprint(web_routes)

def run_flask():
    try:
        # Suppress logging to keep console clean
        log = logging.getLogger("werkzeug")
        log.setLevel(logging.ERROR)
        web_app.logger.setLevel(logging.ERROR)

        # Run the app
        web_app.run(host="0.0.0.0", port=7860)
    except Exception:
        logging.exception("Flask server crashed!")

def start_web_server():
    """Starts the Flask server in a separate daemon thread."""
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
