from datetime import datetime
from app import db


class Progress(db.Model):
    __tablename__ = 'progress'
    id = db.Column(db.Integer, primary_key=True)  # ProgressID
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # UserID
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)  # CourseID
    lessons_completed = db.Column(db.Integer, default=0)  # LessonsCompleted
    total_lessons = db.Column(db.Integer, default=0)  # TotalLessons
    progress_percent = db.Column(db.Integer, default=0)  # ProgressPercent
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)  # LastUpdated
