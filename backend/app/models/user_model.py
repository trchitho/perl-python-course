from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    """User model aligned with generic schema.

    - For SQLite/MySQL: table name is `users` with snake_case columns.
    - For MSSQL deployments with existing tables, controllers use MSSQL-specific
      raw SQL where casing differs, so ORM does not rely on MSSQL table names.
    """

    __tablename__ = 'Users'  # PascalCase for MSSQL

    id = db.Column('UserID', db.Integer, primary_key=True)  # UserID
    fullname = db.Column('FullName', db.String(100), nullable=False)  # FullName
    email = db.Column('Email', db.String(100), unique=True, nullable=False)  # Email
    password_hash = db.Column('PasswordHash', db.String(255), nullable=False)  # PasswordHash
    role = db.Column('Role', db.String(20), nullable=False, default='student')  # Role
    # is_active = db.Column(db.Boolean, default=True, nullable=False)  # Not in original DB schema - commented out
    two_fa_enabled = db.Column('TwoFAEnabled', db.Boolean, default=False)  # TwoFAEnabled (bit in DB)
    avatar_url = db.Column('AvatarUrl', db.String(255))  # AvatarUrl
    created_at = db.Column('CreatedAt', db.DateTime, default=datetime.utcnow)  # CreatedAt
    updated_at = db.Column('UpdatedAt', db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # UpdatedAt

    # Relationship to courses taught by the user
    courses = db.relationship('Course', backref='teacher', lazy=True, foreign_keys='Course.teacher_id')

    # Relationship to enrollments made by the user
    enrollments = db.relationship('Enrollment', back_populates='student', lazy=True, cascade="all, delete-orphan", foreign_keys='Enrollment.student_id')

    # Relationship to announcements made by the user (as a teacher)
    # Temporarily disabled until Announcements table is created
    # announcements = db.relationship('Announcement', back_populates='teacher', lazy=True, cascade="all, delete-orphan")

    # Relationship to quiz results submitted by the user
    quiz_results = db.relationship('QuizResult', back_populates='user', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
