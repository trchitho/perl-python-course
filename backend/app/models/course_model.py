from datetime import datetime
from app import db


class Course(db.Model):
    __tablename__ = 'Courses'  # PascalCase for MSSQL
    id = db.Column('CourseID', db.Integer, primary_key=True)  # CourseID
    name = db.Column('Title', db.String(150), nullable=False)  # Title (mapped to name in code)
    description = db.Column('Description', db.Text)  # Description
    category = db.Column('Category', db.String(50))  # Category
    duration = db.Column('Duration', db.Integer)  # Duration
    teacher_id = db.Column('TeacherID', db.Integer, db.ForeignKey('Users.UserID'), nullable=False)  # TeacherID
    status = db.Column('Status', db.String(20), default='active')  # Status
    created_at = db.Column('CreatedAt', db.DateTime, default=datetime.utcnow)  # CreatedAt

    enrollments = db.relationship('Enrollment', back_populates='course', lazy=True, cascade="all, delete-orphan")
    # Temporarily disabled until Announcements table is created
    # announcements = db.relationship('Announcement', back_populates='course', lazy=True, cascade="all, delete-orphan")
    quizzes = db.relationship('Quiz', back_populates='course', lazy=True, cascade="all, delete-orphan")
    lessons = db.relationship('Lesson', backref='course', lazy=True, cascade="all, delete-orphan")
