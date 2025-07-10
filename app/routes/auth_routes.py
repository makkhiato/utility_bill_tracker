from flask import Blueprint, request, jsonify
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                get_jwt_identity, jwt_required)
from app.models import User, UserSettings
from app.extensions import db

auth_bp = Blueprint('auth',__name__)

@auth_bp.route('/register',methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({'error':'All fields are required'}),400

    if User.query.filter_by(email=email).first():
        return jsonify({'error':'Email already registered'}),409

    new_user = User(name=name, email=email)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    default_settings = UserSettings(user_id=new_user.id)
    db.session.add(default_settings)
    db.session.commit()

    return jsonify({'message':'User registered successfully'}),201

@auth_bp.route('/login',methods=['POST'])
def login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error':'Email and password required'}),400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({'error':'Invalid credentials'}), 401

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 200

@auth_bp.route('/refresh',methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)

    return jsonify({'access_token':new_access_token}), 200

@auth_bp.route('/logout', methods=['POST'])
def logout():
    response = jsonify({'msg': 'Logout successful'})
    return response, 200