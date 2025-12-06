from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.services.jwt_service import require_roles
from app.controllers.student_quiz_controller import (
    list_quizzes_for_course, list_quizzes_for_lesson, get_quiz_detail, submit_quiz, list_quiz_results_for_student, list_progress_for_student,
)
from flask_cors import cross_origin

quiz_bp = Blueprint('quiz_v2', __name__)


@quiz_bp.route('/progress', methods=['GET','OPTIONS'])
@cross_origin(origins='*', allow_headers=['Content-Type','Authorization'], methods=['GET','OPTIONS'])
@jwt_required()
@require_roles('student','admin')
def student_progress():
    return list_progress_for_student()


# Student quiz endpoints
@quiz_bp.route('/courses/<int:course_id>/quizzes', methods=['GET', 'OPTIONS'])
@cross_origin(origins='*', allow_headers=['Content-Type','Authorization'], methods=['GET','OPTIONS'])
@jwt_required()
@require_roles('student','admin')
def student_list_quizzes(course_id):
    return list_quizzes_for_course(course_id)


@quiz_bp.route('/lessons/<int:lesson_id>/quizzes', methods=['GET', 'OPTIONS'])
@cross_origin(origins='*', allow_headers=['Content-Type','Authorization'], methods=['GET','OPTIONS'])
@jwt_required()
@require_roles('student','admin')
def student_list_lesson_quizzes(lesson_id):
    return list_quizzes_for_lesson(lesson_id)


@quiz_bp.route('/quizzes/<int:quiz_id>', methods=['GET', 'OPTIONS'])
@cross_origin(origins='*', allow_headers=['Content-Type','Authorization'], methods=['GET','OPTIONS'])
@jwt_required()
@require_roles('student','admin')
def student_get_quiz(quiz_id):
    return get_quiz_detail(quiz_id)


@quiz_bp.route('/quizzes/<int:quiz_id>/submit', methods=['POST','OPTIONS'])
@cross_origin(origins='*', allow_headers=['Content-Type','Authorization'], methods=['POST','OPTIONS'])
@jwt_required()
@require_roles('student','admin')
def student_submit_quiz(quiz_id):
    data = request.get_json() or {}
    return submit_quiz(quiz_id, data.get('answers') or {})


@quiz_bp.route('/quizzes/results', methods=['GET','OPTIONS'])
@cross_origin(origins='*', allow_headers=['Content-Type','Authorization'], methods=['GET','OPTIONS'])
@jwt_required()
@require_roles('student','admin')
def student_results():
    return list_quiz_results_for_student()
