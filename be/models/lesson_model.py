from extensions import db
from datetime import datetime

class Lesson(db.Model):
    __tablename__ = "lessons"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    quiz = db.Column(db.Text) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
