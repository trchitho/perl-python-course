from flask import Blueprint, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from flask_cors import cross_origin
from app.controllers.teacher_controller import (
    stats_for_teacher,
    list_courses, create_course, update_course, delete_course, toggle_course_status,
    list_lessons, create_lesson, reorder_lessons, update_lesson, delete_lesson,
    list_quiz_results, list_questions, create_question, list_quizzes, create_quiz, update_quiz, delete_quiz, update_question, delete_question,
    list_all_quizzes_for_teacher,
    list_subscribers, approve_subscriber, reject_subscriber, remove_subscriber, get_student_progress,
    list_course_scores,
    import_quiz_questions,
)

teacher_bp = Blueprint('teacher_v2', __name__)


def _require_teacher():
    claims = get_jwt() or {}
    return claims.get('role') in ('teacher', 'admin')


@teacher_bp.before_request
def _guard():
    if request.method == 'OPTIONS':
        return None
    verify_jwt_in_request()
    if not _require_teacher():
        return {'error': 'forbidden'}, 403


@teacher_bp.after_request
def _corsify(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
    return response


@teacher_bp.route('/stats', methods=['GET', 'OPTIONS'])
@cross_origin(origins='*', allow_headers=['Content-Type','Authorization'], methods=['GET','OPTIONS'])
def stats():
    return stats_for_teacher()


# Courses
@teacher_bp.route('/courses', methods=['GET', 'POST'])
def courses():
    if request.method == 'GET':
        return list_courses()
    return create_course(request.get_json() or {})


@teacher_bp.route('/courses/<int:course_id>', methods=['PUT', 'DELETE'])
def course_detail(course_id):
    if request.method == 'PUT':
        return update_course(course_id, request.get_json() or {})
    return delete_course(course_id)


@teacher_bp.route('/courses/<int:course_id>/status', methods=['PATCH'])
def course_status(course_id):
    data = request.get_json() or {}
    return toggle_course_status(course_id, data.get('status', 'draft'))


# Lessons
@teacher_bp.route('/courses/<int:course_id>/lessons', methods=['GET', 'POST'])
def course_lessons(course_id):
    if request.method == 'GET':
        return list_lessons(course_id)
    return create_lesson(course_id, request.get_json() or {})


@teacher_bp.route('/courses/<int:course_id>/lessons/reorder', methods=['PATCH'])
def course_lessons_reorder(course_id):
    data = request.get_json() or {}
    return reorder_lessons(course_id, data.get('order') or [])


# Quizzes
@teacher_bp.route('/courses/<int:course_id>/quizzes', methods=['GET', 'POST'])
def course_quizzes(course_id):
    if request.method == 'GET':
        return list_quizzes(course_id)
    return create_quiz(course_id, request.get_json() or {})


@teacher_bp.route('/courses/<int:course_id>/scores', methods=['GET'])
def course_scores(course_id):
    return list_course_scores(course_id)

@teacher_bp.route('/quizzes', methods=['GET'])
def teacher_all_quizzes():
    return list_all_quizzes_for_teacher()

@teacher_bp.route('/quizzes/<int:quiz_id>/questions', methods=['GET', 'POST'])
def quiz_questions(quiz_id):
    if request.method == 'GET':
        return list_questions(quiz_id)
    return create_question(quiz_id, request.get_json() or {})


@teacher_bp.route('/quizzes/<int:quiz_id>/import', methods=['POST'])
def import_questions(quiz_id):
    """Import questions from uploaded Word file"""
    data = request.get_json() or {}
    file_path = data.get('file_path')
    if not file_path:
        return {'error': 'file_path is required'}, 400
    return import_quiz_questions(quiz_id, file_path)


@teacher_bp.route('/quizzes/<int:quiz_id>/results', methods=['GET'])
def quiz_results(quiz_id):
    return list_quiz_results(quiz_id)


# Update/Delete lessons
@teacher_bp.route('/lessons/<int:lesson_id>', methods=['PUT', 'DELETE'])
def lesson_ops(lesson_id):
    if request.method == 'PUT':
        return update_lesson(lesson_id, request.get_json() or {})
    return delete_lesson(lesson_id)


# Update/Delete quizzes
@teacher_bp.route('/quizzes/<int:quiz_id>', methods=['PUT', 'DELETE'])
def quiz_ops(quiz_id):
    if request.method == 'PUT':
        return update_quiz(quiz_id, request.get_json() or {})
    return delete_quiz(quiz_id)


# Update/Delete questions
@teacher_bp.route('/questions/<int:question_id>', methods=['PUT', 'DELETE'])
def question_ops(question_id):
    if request.method == 'PUT':
        return update_question(question_id, request.get_json() or {})
    return delete_question(question_id)


# Subscribers
@teacher_bp.route('/courses/<int:course_id>/subscribers', methods=['GET'])
def subscribers(course_id):
    return list_subscribers(course_id)


@teacher_bp.route('/courses/<int:course_id>/progress/<int:student_id>', methods=['GET'])
def student_progress(course_id, student_id):
    return get_student_progress(course_id, student_id)


@teacher_bp.route('/subscribers/<int:enroll_id>/approve', methods=['POST'])
def sub_approve(enroll_id):
    return approve_subscriber(enroll_id)


@teacher_bp.route('/subscribers/<int:enroll_id>/reject', methods=['POST'])
def sub_reject(enroll_id):
    return reject_subscriber(enroll_id)


@teacher_bp.route('/subscribers/<int:enroll_id>', methods=['DELETE'])
def sub_remove(enroll_id):
    return remove_subscriber(enroll_id)
