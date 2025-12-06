"""
Placement Test View
Routes for placement test functionality
"""
from flask import Blueprint
from flask_jwt_extended import jwt_required
from app.services.jwt_service import require_roles
from app.controllers.placement_test_controller import (
    get_questions, submit_test, get_user_test_history, get_test_result
)

placement_test_bp = Blueprint('placement_test', __name__)


@placement_test_bp.route('/placement-test/questions', methods=['GET'])
@jwt_required()
@require_roles('student', 'teacher', 'admin')
def get_questions_route():
    """Get placement test questions"""
    return get_questions()


@placement_test_bp.route('/placement-test/submit', methods=['POST'])
@jwt_required()
@require_roles('student', 'teacher', 'admin')
def submit_test_route():
    """Submit placement test answers"""
    return submit_test()


@placement_test_bp.route('/placement-test/history', methods=['GET'])
@jwt_required()
@require_roles('student', 'teacher', 'admin')
def get_history_route():
    """Get user's test history"""
    return get_user_test_history()


@placement_test_bp.route('/placement-test/result/<int:test_id>', methods=['GET'])
@jwt_required()
@require_roles('student', 'teacher', 'admin')
def get_result_route(test_id):
    """Get specific test result"""
    return get_test_result(test_id)
