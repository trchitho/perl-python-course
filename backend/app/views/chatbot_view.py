from flask import Blueprint
from app.controllers.chatbot_controller import chat

chatbot_bp = Blueprint('chatbot_v2', __name__)


@chatbot_bp.route('/chat', methods=['POST'])
def chat_view():
    return chat()

