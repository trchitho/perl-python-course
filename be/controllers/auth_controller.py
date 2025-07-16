from models.user_model import User
from extensions import db
from flask_jwt_extended import create_access_token
from flask import jsonify

def register_user(data):
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email đã được đăng ký'}), 400

    role = data.get('role', 'student')
    if role not in ['student', 'teacher']:
        return jsonify({'message': 'Role không hợp lệ'}), 400

    department = data.get('department') if role == 'teacher' else None

    user = User(fullname=data['fullname'], email=data['email'], role=role, department=data.get('department') if role == 'teacher' else None,)
    user.set_password(data['password'])

    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'Đăng ký thành công'}), 201

def login_user(data):
    user = User.query.filter_by(email=data['email']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({'message': 'Sai email hoặc mật khẩu'}), 401

    token = create_access_token(
    identity=str(user.id),
    additional_claims={"role": user.role}
    )
    return jsonify({'token': token, 'fullname': user.fullname, 'role': user.role}), 200
