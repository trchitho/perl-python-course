from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import text
from app import db

profile_bp = Blueprint('profile_v1', __name__)


def _current_user_id() -> int:
    return int(get_jwt_identity())


@profile_bp.route('/me', methods=['GET'])
@jwt_required()
def me_get():
    uid = _current_user_id()
    if db.get_engine().dialect.name == 'mssql':
        row = db.session.execute(text(
            'SELECT [UserID],[FullName],[Email],[Role],[TwoFAEnabled],[AvatarUrl] FROM [dbo].[Users] WHERE [UserID]=:id'
        ), {'id': uid}).fetchone()
        if not row:
            return jsonify({'error': 'not found'}), 404
        return jsonify({'id': row[0], 'fullname': row[1], 'email': row[2], 'role': row[3], 'two_fa_enabled': bool(row[4]) if row[4] is not None else False, 'avatar_url': row[5] or ''})
    # generic ORM path
    from app.models.user_model import User
    u = User.query.get(uid)
    if not u:
        return jsonify({'error': 'not found'}), 404
    return jsonify({'id': u.id, 'fullname': u.fullname, 'email': u.email, 'role': u.role, 'two_fa_enabled': bool(getattr(u, 'two_fa_enabled', False)), 'avatar_url': getattr(u, 'avatar_url', '') or ''})


@profile_bp.route('/me', methods=['PUT'])
@jwt_required()
def me_update():
    uid = _current_user_id()
    data = request.get_json() or {}
    fullname = data.get('fullname')
    avatar_url = data.get('avatar_url')
    if db.get_engine().dialect.name == 'mssql':
        sets = []
        params = {'id': uid}
        if fullname is not None:
            sets.append('[FullName]=:fn')
            params['fn'] = fullname
        if avatar_url is not None:
            sets.append('[AvatarUrl]=:av')
            params['av'] = avatar_url
        if not sets:
            return jsonify({'message': 'no changes'})
        db.session.execute(text('UPDATE [dbo].[Users] SET ' + ','.join(sets) + ' WHERE [UserID]=:id'), params)
        db.session.commit()
        return jsonify({'message': 'updated'})
    from app.models.user_model import User
    u = User.query.get(uid)
    if not u:
        return jsonify({'error': 'not found'}), 404
    if fullname is not None:
        u.fullname = fullname
    if avatar_url is not None:
        u.avatar_url = avatar_url
    db.session.add(u)
    db.session.commit()
    return jsonify({'message': 'updated'})


@profile_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    uid = _current_user_id()
    data = request.get_json() or {}
    current_pw = data.get('current_password') or ''
    new_pw = data.get('new_password') or ''
    if not new_pw:
        return jsonify({'message': 'new_password required'}), 400
    if db.get_engine().dialect.name == 'mssql':
        row = db.session.execute(text('SELECT [PasswordHash] FROM [dbo].[Users] WHERE [UserID]=:id'), {'id': uid}).fetchone()
        if not row:
            return jsonify({'error': 'not found'}), 404
        pwd_hash = row[0] or ''
        ok = False
        try:
            ok = check_password_hash(pwd_hash, current_pw)
        except Exception:
            ok = (str(pwd_hash) == current_pw)
        if not ok:
            return jsonify({'message': 'incorrect password'}), 400
        db.session.execute(text('UPDATE [dbo].[Users] SET [PasswordHash]=:ph WHERE [UserID]=:id'), {'ph': generate_password_hash(new_pw), 'id': uid})
        db.session.commit()
        return jsonify({'message': 'password updated'})
    from app.models.user_model import User
    u = User.query.get(uid)
    if not u:
        return jsonify({'error': 'not found'}), 404
    if not u.check_password(current_pw):
        return jsonify({'message': 'incorrect password'}), 400
    u.set_password(new_pw)
    db.session.add(u)
    db.session.commit()
    return jsonify({'message': 'password updated'})


@profile_bp.route('/2fa', methods=['POST'])
@jwt_required()
def two_fa_toggle():
    uid = _current_user_id()
    data = request.get_json() or {}
    enabled = bool(data.get('enabled'))
    if db.get_engine().dialect.name == 'mssql':
        try:
            db.session.execute(text('UPDATE [dbo].[Users] SET [TwoFAEnabled]=:v WHERE [UserID]=:id'), {'v': 1 if enabled else 0, 'id': uid})
            db.session.commit()
            return jsonify({'message': '2fa updated', 'enabled': enabled})
        except Exception:
            return jsonify({'message': '2fa not supported on this schema'}), 400
    from app.models.user_model import User
    u = User.query.get(uid)
    if not u:
        return jsonify({'error': 'not found'}), 404
    setattr(u, 'two_fa_enabled', enabled)
    db.session.add(u)
    db.session.commit()
    return jsonify({'message': '2fa updated', 'enabled': enabled})

