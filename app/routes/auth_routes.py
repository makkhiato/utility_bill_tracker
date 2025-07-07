from flask import Blueprint, request, jsonify
from app.models import User
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

    return jsonify({'message':'User registered successfully'}),201

@auth_bp.route('/login',methods=['POST'])
def login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error':'Email and password required'}),400

    user = User.query.filter_by(email=email).first()

    if not user or  not user.check_password(password):
        return jsonify({'error':'Invalid credentials'}), 401

    return jsonify({'message':'Login successful'}), 200