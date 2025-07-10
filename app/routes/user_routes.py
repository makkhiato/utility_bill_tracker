from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.utils.auth import get_current_user
from app.models import User
from app.extensions import db

user_bp = Blueprint('user',__name__)

@user_bp.route('/settings',methods=['GET'])
@jwt_required(refresh=False)
def get_settings():
    user = get_current_user()

    if not user:
        return jsonify(({'error':'Settings not found'})), 404

    settings = {
        'currency': user.settings.currency,
        'dark_mode': user.settings.dark_mode
    }

    return jsonify(settings), 200

@user_bp.route('/settings',methods=['PUT'])
@jwt_required(refresh=False)
def update_settings():
    user = get_current_user()

    if not user or not user.settings:
        return jsonify({'error':'Settings not found'}), 404

    data = request.get_json()

    currency = data.get('currency')
    dark_mode = data.get('dark_mode')

    if currency:
        user.settings.currency = currency

    if dark_mode is not None:
        user.settings.dark_mode = bool(dark_mode)

    db.session.commit()

    return jsonify({'message':'Settings updated successfully'}), 200

@user_bp.route('/user',methods=['PUT'])
@jwt_required(refresh=False)
def update_user():
    user = get_current_user()
    if not user:
        return jsonify({'error':'User not found'}), 404

    data = request.get_json()

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if name:
        user.name = name

    if email:
        if User.query.filter_by(email=email).first() and user.email != email:
            return jsonify({'error':'Email already in use'}), 409

        user.email = email

    if password:
        user.set_password(password)

    db.session.commit()

    return jsonify({'message':'User updated successfully'}), 200