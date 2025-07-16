from flask import Blueprint, request
from controllers.auth_controller import register_user, login_user

auth_bp = Blueprint('auth', __name__)  # ✅ Khai báo trước khi dùng

@auth_bp.route('/register', methods=['POST'])
def register():
    return register_user(request.json)

@auth_bp.route('/login', methods=['POST'])
def login():
    return login_user(request.json)
