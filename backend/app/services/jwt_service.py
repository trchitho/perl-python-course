from flask_jwt_extended import JWTManager, create_access_token, get_jwt
from functools import wraps
from flask import jsonify


def init_jwt(jwt: JWTManager):
    @jwt.user_identity_loader
    def identity(user):
        return str(user)

    @jwt.additional_claims_loader
    def add_claims(identity):
        return {}


def issue_token(user_id, role: str):
    return create_access_token(identity=str(user_id), additional_claims={"role": role})


def require_roles(*roles: str):
    """Decorator to enforce role-based access on a view.

    Usage: @jwt_required() then @require_roles('student','admin')
    """
    def _wrap(fn):
        @wraps(fn)
        def _inner(*args, **kwargs):
            claims = get_jwt() or {}
            if roles and claims.get('role') not in roles:
                return jsonify({'error': 'forbidden'}), 403
            return fn(*args, **kwargs)
        return _inner
    return _wrap
