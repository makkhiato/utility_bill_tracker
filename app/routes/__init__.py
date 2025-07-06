from .auth_routes import auth_bp
from .user_routes import user_bp
from .bill_routes import bill_bp
from .analytics_routes import analytics_bp

def register_routes(app):
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(bill_bp, url_prefix='/api')
    app.register_blueprint(analytics_bp, url_prefix='/api')