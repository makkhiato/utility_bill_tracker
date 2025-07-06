from flask import Flask
from .config import Config
from .extensions import db
from .routes import api_routes
from dotenv import load_dotenv
load_dotenv()

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    app.register_blueprint(api_routes)

    return app