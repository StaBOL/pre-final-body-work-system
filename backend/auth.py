from flask import request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from backend.db import get_db, query_one, execute

def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'msg': 'Email and password required'}), 400
    db = get_db()
    existing = query_one('SELECT id FROM user WHERE email = ?', (email,))
    if existing:
        return jsonify({'msg': 'User already exists'}), 409
    hashed = generate_password_hash(password)
    execute('INSERT INTO user (email, password) VALUES (?, ?)', (email, hashed))
    return jsonify({'msg': 'User created successfully'}), 201

def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = query_one('SELECT id, password FROM user WHERE email = ?', (email,))
    if not user or not check_password_hash(user['password'], password):
        return jsonify({'msg': 'Invalid credentials'}), 401
    access_token = create_access_token(identity=str(user['id']))
    return jsonify({'access_token': access_token, 'user_id': user['id'], 'role': 'student'})