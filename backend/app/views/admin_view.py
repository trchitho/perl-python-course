from flask import Blueprint, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from flask_cors import cross_origin
from app.controllers.admin_controller import (
    list_users, lock_user, unlock_user,
    create_user, update_user, delete_user, set_role,
    admin_stats,
    list_enrollments_admin, approve_enrollment_admin, lock_enrollment_admin,
    get_settings, update_settings, run_backup_job,
    list_logs, export_logs,
)

admin_bp = Blueprint('admin_v2', __name__)


def _require_admin():
    claims = get_jwt() or {}
    if claims.get('role') != 'admin':
        return {'error':'forbidden'}, 403


@admin_bp.before_request
def _guard():
    # Allow CORS preflight
    if request.method == 'OPTIONS':
        return None
    # Enforce JWT and admin role for real requests
    verify_jwt_in_request()
    forbidden = _require_admin()
    if forbidden:
        return forbidden


@admin_bp.after_request
def _corsify(response):
    # Ensure CORS headers are present even on errors
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
    return response


@admin_bp.route('/users', methods=['GET'])
def users():
    return list_users()


@admin_bp.route('/users', methods=['POST'])
def users_create():
    return create_user(request.get_json() or {})


@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
def users_update(user_id):
    return update_user(user_id, request.get_json() or {})


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
def users_delete(user_id):
    return delete_user(user_id)


@admin_bp.route('/users/<int:user_id>/role', methods=['PATCH'])
def users_set_role(user_id):
    data = request.get_json() or {}
    return set_role(user_id, data.get('role', 'student'))


@admin_bp.route('/users/<int:user_id>/lock', methods=['POST'])
def lock(user_id):
    return lock_user(user_id)


@admin_bp.route('/users/<int:user_id>/unlock', methods=['POST'])
def unlock(user_id):
    return unlock_user(user_id)


@admin_bp.route('/stats', methods=['GET', 'OPTIONS'])
@cross_origin(origins='*', allow_headers=['Content-Type','Authorization'], methods=['GET','OPTIONS'])
def stats():
    return admin_stats()


@admin_bp.route('/enrollments', methods=['GET', 'OPTIONS'])
@cross_origin(origins='*', allow_headers=['Content-Type','Authorization'], methods=['GET','OPTIONS'])
def enrollments():
    return list_enrollments_admin()


@admin_bp.route('/enrollments/<int:en_id>/approve', methods=['POST'])
def enroll_approve(en_id):
    return approve_enrollment_admin(en_id)


@admin_bp.route('/enrollments/<int:en_id>/lock', methods=['POST'])
def enroll_lock(en_id):
    return lock_enrollment_admin(en_id)


@admin_bp.route('/settings', methods=['GET'])
def settings_get():
    return get_settings()


@admin_bp.route('/settings', methods=['PUT'])
def settings_put():
    return update_settings(request.get_json() or {})


@admin_bp.route('/backup', methods=['POST'])
def backup():
    return run_backup_job()


@admin_bp.route('/logs', methods=['GET'])
def logs():
    return list_logs()


@admin_bp.route('/logs/export')
def logs_export():
    fmt = request.args.get('format','csv')
    return export_logs(fmt)
