from flask import Blueprint
from flask_jwt_extended import jwt_required
from app.services.jwt_service import require_roles
from app.controllers.chatbot_controller import chat, get_history, clear_history, get_session_messages

chatbot_bp = Blueprint('chatbot_v2', __name__)


@chatbot_bp.route('/chat', methods=['POST'])
@jwt_required()
@require_roles('student', 'teacher', 'admin')
def chat_view():
    return chat()


@chatbot_bp.route('/history', methods=['GET'])
@jwt_required()
@require_roles('student', 'teacher', 'admin')
def history_view():
    return get_history()


@chatbot_bp.route('/history/<session_id>', methods=['GET'])
@jwt_required()
@require_roles('student', 'teacher', 'admin')
def session_messages_view(session_id):
    return get_session_messages(session_id)


@chatbot_bp.route('/history', methods=['DELETE'])
@jwt_required()
@require_roles('student', 'teacher', 'admin')
def clear_history_view():
    return clear_history()

