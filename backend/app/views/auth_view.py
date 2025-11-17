from flask import Blueprint, request, jsonify
from app import db
from app.models.user_model import User
from app.services.jwt_service import issue_token
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth_v2', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip()
    fullname = (data.get('fullname') or 'User').strip()
    password = data.get('password') or '123456'
    role = data.get('role') or 'student'
    if role not in ['student','teacher','admin']:
        return jsonify({'message': 'Invalid role'}), 400

    if db.get_engine().dialect.name == 'mssql':
        exists = db.session.execute(text('SELECT 1 FROM [dbo].[Users] WHERE [Email]=:e'), {'e': email}).fetchone()
        if exists:
            return jsonify({'message': 'Email is already registered'}), 400
        pwd_hash = generate_password_hash(password)
        try:
            row = db.session.execute(text(
                'INSERT INTO [dbo].[Users] (FullName,Email,PasswordHash,Role,TwoFAEnabled,CreatedAt,UpdatedAt) '
                'OUTPUT INSERTED.UserID VALUES (:fn,:em,:ph,:rl,0,GETDATE(),GETDATE())'
            ), {'fn': fullname, 'em': email, 'ph': pwd_hash, 'rl': role}).fetchone()
        except Exception:
            # Minimal column set fallback
            row = db.session.execute(text(
                'INSERT INTO [dbo].[Users] (FullName,Email,PasswordHash,Role) OUTPUT INSERTED.UserID VALUES (:fn,:em,:ph,:rl)'
            ), {'fn': fullname, 'em': email, 'ph': pwd_hash, 'rl': role}).fetchone()
        db.session.commit()
        return jsonify({'message': 'Registration successful', 'id': int(row[0])}), 201

    # Generic ORM path
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email is already registered'}), 400
    u = User(fullname=fullname, email=email, role=role)
    u.set_password(password)
    db.session.add(u)
    db.session.commit()
    return jsonify({'message': 'Registration successful'}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip()
    password = data.get('password') or ''

    if db.get_engine().dialect.name == 'mssql':
        row = None
        try:
            row = db.session.execute(text(
                'SELECT [UserID],[FullName],[Email],[PasswordHash],[Role],[IsActive] FROM [dbo].[Users] WHERE [Email]=:em'
            ), {'em': email}).fetchone()
        except Exception:
            row = db.session.execute(text(
                'SELECT [UserID],[FullName],[Email],[PasswordHash],[Role] FROM [dbo].[Users] WHERE [Email]=:em'
            ), {'em': email}).fetchone()
        if not row:
            return jsonify({'message': 'Incorrect email or password'}), 401
        uid, fullname, _, pwd_hash, role, *rest = row
        is_active = True
        if rest:
            try:
                is_active = bool(rest[0])
            except Exception:
                is_active = True
        ok = False
        if pwd_hash:
            try:
                ok = check_password_hash(pwd_hash, password)
            except Exception:
                ok = False
        if not ok and pwd_hash:
            # fallback if stored plain text (not recommended)
            ok = (password == str(pwd_hash))
        if not ok:
            return jsonify({'message': 'Incorrect email or password'}), 401
        if is_active is False:
            return jsonify({'message': 'Account is locked'}), 403
        token = issue_token(uid, role or 'student')
        return jsonify({'token': token, 'fullname': fullname, 'role': role or 'student', 'email': email}), 200

    # Generic ORM path
    u = User.query.filter_by(email=email).first()
    if not u or not u.check_password(password):
        return jsonify({'message': 'Incorrect email or password'}), 401
    if getattr(u, 'is_active', True) is False:
        return jsonify({'message': 'Account is locked'}), 403
    token = issue_token(u.id, u.role)
    return jsonify({'token': token, 'fullname': u.fullname, 'role': u.role, 'email': u.email}), 200
