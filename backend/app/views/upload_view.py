"""
Upload View
Routes for file upload functionality
"""
from flask import Blueprint
from flask_jwt_extended import jwt_required
from app.services.jwt_service import require_roles
from app.controllers.upload_controller import (
    upload_file, upload_lesson_material, delete_uploaded_file,
    get_upload_limits, get_stats
)

upload_bp = Blueprint('upload', __name__)


@upload_bp.route('/upload', methods=['POST'])
@jwt_required()
@require_roles('teacher', 'admin')
def upload_file_route():
    """Upload file (teacher/admin only)"""
    return upload_file()


@upload_bp.route('/upload/lesson', methods=['POST'])
@jwt_required()
@require_roles('teacher', 'admin')
def upload_lesson_material_route():
    """Upload lesson material (teacher/admin only)"""
    return upload_lesson_material()


@upload_bp.route('/upload/delete', methods=['DELETE'])
@jwt_required()
@require_roles('teacher', 'admin')
def delete_file_route():
    """Delete uploaded file (teacher/admin only)"""
    return delete_uploaded_file()


@upload_bp.route('/upload/limits', methods=['GET'])
def get_limits_route():
    """Get upload size limits (public)"""
    return get_upload_limits()


@upload_bp.route('/upload/stats', methods=['GET'])
@jwt_required()
@require_roles('admin')
def get_stats_route():
    """Get upload statistics (admin only)"""
    return get_stats()
