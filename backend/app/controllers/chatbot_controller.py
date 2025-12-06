from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity
from app import db
from app.models.chatbot_history_model import ChatbotHistory
from sqlalchemy import func
import os
import uuid
import google.generativeai as genai


def get_gemini_response(message):
    """Get response from Google Gemini API"""
    try:
        # Get API key from environment
        api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            return "⚠️ Gemini API key chưa được cấu hình. Vui lòng thêm GEMINI_API_KEY vào file .env"
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Use gemini-2.5-flash (latest stable model)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Generate response
        response = model.generate_content(message)
        return response.text
        
    except Exception as e:
        print(f"[Error] Gemini API failed: {e}")
        return f"❌ Lỗi kết nối đến Gemini API: {str(e)}\n\nVui lòng kiểm tra API key hoặc kết nối internet."


def chat():
    """Handle chat request - connect to Gemini API and return response"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    msg = (data.get('message') or '').strip()
    session_id = data.get('session_id')
    
    if not msg:
        return jsonify({'error': 'Message is required'}), 400
    
    # Create new session if not provided
    if not session_id:
        session_id = str(uuid.uuid4())
    
    # Get response from Gemini API
    answer = get_gemini_response(msg)
    
    # Save to history
    try:
        history = ChatbotHistory(
            user_id=user_id,
            session_id=session_id,
            question=msg,
            answer=answer
        )
        db.session.add(history)
        db.session.commit()
    except Exception as e:
        print(f"[Warning] Failed to save chat history: {e}")
    
    # Ensure UTF-8 encoding for Vietnamese text
    response_data = {
        'response': answer,
        'session_id': session_id
    }
    return jsonify(response_data), 200, {'Content-Type': 'application/json; charset=utf-8'}


def get_history():
    """Get chat history grouped by sessions for current user"""
    user_id = int(get_jwt_identity())
    
    try:
        # Get all sessions with their first question and latest timestamp
        sessions = db.session.query(
            ChatbotHistory.session_id,
            func.min(ChatbotHistory.question).label('first_question'),
            func.max(ChatbotHistory.created_at).label('last_updated'),
            func.count(ChatbotHistory.id).label('message_count')
        ).filter_by(user_id=user_id)\
         .group_by(ChatbotHistory.session_id)\
         .order_by(func.max(ChatbotHistory.created_at).desc())\
         .limit(50)\
         .all()
        
        return jsonify([{
            'session_id': s.session_id,
            'title': s.first_question[:50] + '...' if len(s.first_question) > 50 else s.first_question,
            'last_updated': s.last_updated.isoformat() if s.last_updated else '',
            'message_count': s.message_count
        } for s in sessions])
    except Exception as e:
        print(f"[Warning] Failed to load chat history: {e}")
        return jsonify([])


def get_session_messages(session_id):
    """Get all messages in a specific session"""
    user_id = int(get_jwt_identity())
    
    try:
        messages = ChatbotHistory.query.filter_by(
            user_id=user_id,
            session_id=session_id
        ).order_by(ChatbotHistory.created_at.asc()).all()
        
        return jsonify([{
            'id': m.id,
            'question': m.question,
            'answer': m.answer,
            'created_at': m.created_at.isoformat() if m.created_at else ''
        } for m in messages])
    except Exception as e:
        print(f"[Warning] Failed to load session messages: {e}")
        return jsonify([])


def clear_history():
    """Clear all chat history for current user"""
    user_id = int(get_jwt_identity())
    
    try:
        ChatbotHistory.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        return jsonify({'message': 'Chat history cleared successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
