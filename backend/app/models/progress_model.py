from datetime import datetime
from app import db


class Progress(db.Model):
    __tablename__ = 'Progress'  # PascalCase for MSSQL
    id = db.Column('ProgressID', db.Integer, primary_key=True)  # ProgressID
    student_id = db.Column('UserID', db.Integer, db.ForeignKey('Users.UserID'), nullable=False)  # UserID (not student_id!)
    course_id = db.Column('CourseID', db.Integer, db.ForeignKey('Courses.CourseID'), nullable=False)  # CourseID
    lessons_completed = db.Column('LessonsCompleted', db.Integer, default=0)  # LessonsCompleted
    total_lessons = db.Column('TotalLessons', db.Integer, default=0)  # TotalLessons
    progress_percent = db.Column('ProgressPercent', db.Integer)  # ProgressPercent (computed column in DB)
    last_updated = db.Column('LastUpdated', db.DateTime, default=datetime.utcnow)  # LastUpdated
