from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt
from app.services.jwt_service import require_roles
from app.controllers.announcement_controller import (
    teacher_create_announcement,
    teacher_list_announcements,
    student_list_announcements,
)

ann_bp = Blueprint('ann_v2', __name__)


def _role():
    claims = get_jwt() or {}
    return claims.get('role')


@ann_bp.route('/teacher/announcements', methods=['POST', 'GET'])
@jwt_required()
def teacher_announcements():
    if _role() != 'teacher' and _role() != 'admin':
        return {'error': 'forbidden'}, 403
    if request.method == 'POST':
        return teacher_create_announcement(request.get_json() or {})
    # GET
    course_id = request.args.get('course_id', type=int)
    return teacher_list_announcements(course_id)


@ann_bp.route('/student/announcements', methods=['GET'])
@jwt_required()
@require_roles('student','admin')
def student_announcements():
    course_id = request.args.get('course_id', type=int)
    return student_list_announcements(course_id)
