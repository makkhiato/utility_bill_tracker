from flask_jwt_extended import get_jwt_identity
from app.models import User
from flask import abort

def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        abort(401, description='Invalid or expired token')
    return user