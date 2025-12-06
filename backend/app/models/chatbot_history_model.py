from datetime import datetime
from app import db
from sqlalchemy import UnicodeText


class ChatbotHistory(db.Model):
    __tablename__ = 'ChatbotHistory'  # PascalCase for MSSQL
    id = db.Column('ChatID', db.Integer, primary_key=True)  # ChatID
    user_id = db.Column('UserID', db.Integer, db.ForeignKey('Users.UserID'), nullable=False)  # UserID
    session_id = db.Column('SessionID', db.String(50))  # SessionID for grouping conversations
    question = db.Column('Question', UnicodeText)  # Question - Use UnicodeText for Vietnamese
    answer = db.Column('Answer', UnicodeText)  # Answer - Use UnicodeText for Vietnamese
    created_at = db.Column('CreatedAt', db.DateTime, default=datetime.utcnow)  # CreatedAt

