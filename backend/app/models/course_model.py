from datetime import datetime
from app import db


class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)  # CourseID
    name = db.Column(db.String(200), nullable=False)  # Title
    description = db.Column(db.Text)  # Description
    category = db.Column(db.String(100))  # Category
    duration = db.Column(db.Integer)  # Duration (minutes or hours)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # TeacherID
    status = db.Column(db.String(30), default='active')  # Status
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # CreatedAt
