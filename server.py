# server.py
import logging
import threading
from flask import Flask
from config import PORT

# Initialize Flask
web_app = Flask(__name__)

# Silence Flask Logs (optional, keeps terminal clean)
log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)
web_app.logger.setLevel(logging.ERROR)

@web_app.route("/")
def hello_world():
    return "Bot is running!", 200

def run_flask():
    try:
        # 0.0.0.0 is required for cloud deployments
        web_app.run(host="0.0.0.0", port=PORT)
    except Exception as e:
        print(f"Flask server crashed: {e}")

def start_server():
    """
    Starts the Flask server in a separate thread so it doesn't block the Bot.
    """
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
