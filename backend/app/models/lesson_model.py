from datetime import datetime
from app import db


class Lesson(db.Model):
    __tablename__ = 'lessons'
    id = db.Column(db.Integer, primary_key=True)  # LessonID
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)  # CourseID
    title = db.Column(db.String(200), nullable=False)  # Title
    video_url = db.Column(db.Text)  # VideoUrl
    file_url = db.Column(db.Text)  # FileUrl
    description = db.Column(db.Text)  # Description
    order_index = db.Column(db.Integer)  # OrderIndex
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # CreatedAt
    # Legacy fields for compatibility
    content = db.Column(db.Text)
    quiz = db.Column(db.Text)
