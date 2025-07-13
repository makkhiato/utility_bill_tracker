from flask import Flask
from .config import Config
from .extensions import db, jwt, scheduler
from .routes import register_routes
from app.utils.scheduled_notif import notify_upcoming_bills
from dotenv import load_dotenv
load_dotenv()

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    scheduler.init_app(app)
    scheduler.start()
    register_routes(app)

    scheduler.add_job(
        id='notify_bills',
        func=notify_upcoming_bills,
        trigger='cron',
        hour=7
    )

    with app.app_context():
        from . import models
        db.create_all()

    return app