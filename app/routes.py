from flask import Blueprint

api_routes = Blueprint('api_routes',__name__)

@api_routes.route('/')
def home():
    return 'Welcome to the Utility Bill Tracker Mobile API!'