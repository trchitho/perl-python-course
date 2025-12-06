from datetime import datetime
from app import db


class Lesson(db.Model):
    __tablename__ = 'Lessons'  # PascalCase for MSSQL
    id = db.Column('LessonID', db.Integer, primary_key=True)  # LessonID
    course_id = db.Column('CourseID', db.Integer, db.ForeignKey('Courses.CourseID'), nullable=False)  # CourseID
    title = db.Column('Title', db.String(150), nullable=False)  # Title
    video_url = db.Column('VideoUrl', db.String(255))  # VideoUrl
    file_url = db.Column('FileUrl', db.String(255))  # FileUrl
    quizzes = db.relationship('Quiz', back_populates='lesson', lazy=True)
    description = db.Column('Description', db.Text)  # Description
    order_index = db.Column('OrderIndex', db.Integer, default=1)  # OrderIndex
    created_at = db.Column('CreatedAt', db.DateTime, default=datetime.utcnow)  # CreatedAt
    # Legacy fields for compatibility
    content = db.Column('Content', db.Text)  # Content
    # quiz = db.Column('Quiz', db.Text)  # Quiz (legacy) - Not in DB schema, commented out
