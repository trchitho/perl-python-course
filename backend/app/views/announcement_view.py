from flask import Blueprint
from flask_jwt_extended import jwt_required
from app.services.jwt_service import require_roles
from app.controllers.announcement_controller import (
    get_announcements,
    create_announcement,
    update_announcement,
    delete_announcement,
    get_announcement_detail
)

announcement_bp = Blueprint('announcements', __name__)


@announcement_bp.route('', methods=['GET'])
@jwt_required()
def announcements_list():
    """Get all announcements for current user"""
    return get_announcements()


@announcement_bp.route('/<int:announcement_id>', methods=['GET'])
@jwt_required()
def announcement_detail(announcement_id):
    """Get single announcement"""
    return get_announcement_detail(announcement_id)


@announcement_bp.route('', methods=['POST'])
@jwt_required()
@require_roles('teacher', 'admin')
def create_announcement_view():
    """Create new announcement (Teacher/Admin only)"""
    return create_announcement()


@announcement_bp.route('/<int:announcement_id>', methods=['PUT'])
@jwt_required()
@require_roles('teacher', 'admin')
def update_announcement_view(announcement_id):
    """Update announcement (Teacher/Admin only)"""
    return update_announcement(announcement_id)


@announcement_bp.route('/<int:announcement_id>', methods=['DELETE'])
@jwt_required()
@require_roles('teacher', 'admin')
def delete_announcement_view(announcement_id):
    """Delete announcement (Teacher/Admin only)"""
    return delete_announcement(announcement_id)
