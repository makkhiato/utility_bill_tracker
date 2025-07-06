from flask import Flask
from .config import Config
from .extensions import db, migrate
from .routes import register_routes
from dotenv import load_dotenv
load_dotenv()

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app,db)
    register_routes(app)

    with app.app_context():
        from . import models
        db.create_all()

    return app