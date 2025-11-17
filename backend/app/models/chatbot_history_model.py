from datetime import datetime
from app import db


class ChatbotHistory(db.Model):
    __tablename__ = 'chatbot_history'
    id = db.Column(db.Integer, primary_key=True)  # ChatID
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # UserID
    question = db.Column(db.Text)
    answer = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

