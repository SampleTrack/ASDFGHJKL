from flask import Blueprint

# Create a Blueprint (a group of routes)
web_routes = Blueprint('web_routes', __name__)

@web_routes.route("/")
def hello_world():
    return "Hello, World! Bot is running."
