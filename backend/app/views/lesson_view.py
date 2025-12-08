from flask import Blueprint, request
from flask_jwt_extended import jwt_required, verify_jwt_in_request
from app.services.jwt_service import require_roles
from app.controllers.lesson_controller import list_all_courses_for_student, enroll, course_detail, lesson_detail

lesson_bp = Blueprint('lesson_v2', __name__)


@lesson_bp.route('/all-courses', methods=['GET'])
@jwt_required()
@require_roles('student','admin')
def all_courses():
    # Get search query from URL parameters
    search_query = request.args.get('search', '').strip()
    return list_all_courses_for_student(search_query=search_query)


@lesson_bp.route('/enroll', methods=['POST'])
@jwt_required()
@require_roles('student','admin')
def enroll_course():
    data = request.get_json() or {}
    cid = data.get('course_id')
    if not cid:
        return {"message": "Missing course_id"}, 400
    return enroll(int(cid))


@lesson_bp.route('/course-detail/<int:course_id>', methods=['GET'])
@jwt_required()
@require_roles('student','admin')
def course_detail_view(course_id):
    return course_detail(course_id)


@lesson_bp.route('/lesson/<int:lesson_id>', methods=['GET'])
@jwt_required()
@require_roles('student','admin')
def lesson_detail_view(lesson_id):
    return lesson_detail(lesson_id)
