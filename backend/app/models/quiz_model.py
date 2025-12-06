from datetime import datetime
from app import db
from app.database_types import UnicodeString, UnicodeTextType


class Quiz(db.Model):
    __tablename__ = 'Quizzes'  # PascalCase for MSSQL
    # Match existing SQL Server schema where PK column is QuizID
    id = db.Column('QuizID', db.Integer, primary_key=True)  # QuizID
    course_id = db.Column('CourseID', db.Integer, db.ForeignKey('Courses.CourseID'), nullable=False)  # CourseID
    lesson_id = db.Column('LessonID', db.Integer, db.ForeignKey('Lessons.LessonID'))  # LessonID
    title = db.Column('Title', UnicodeString(150), nullable=False)  # Title - NVARCHAR(150)
    description = db.Column('Description', UnicodeTextType)  # Description - NVARCHAR(MAX)
    total_questions = db.Column('TotalQuestions', db.Integer, default=0)  # TotalQuestions
    time_limit = db.Column('TimeLimit', db.Integer)  # TimeLimit (minutes)
    created_at = db.Column('CreatedAt', db.DateTime, default=datetime.utcnow)  # CreatedAt

    course = db.relationship('Course', back_populates='quizzes', foreign_keys=[course_id])
    lesson = db.relationship('Lesson', back_populates='quizzes', foreign_keys=[lesson_id])
    questions = db.relationship('QuizQuestion', back_populates='quiz', cascade="all, delete-orphan")
    results = db.relationship('QuizResult', back_populates='quiz', cascade="all, delete-orphan")


class QuizQuestion(db.Model):
    __tablename__ = 'QuizQuestions'  # PascalCase for MSSQL
    id = db.Column('QuestionID', db.Integer, primary_key=True)  # QuestionID
    # Reference quizzes.QuizID to match existing DB
    quiz_id = db.Column('QuizID', db.Integer, db.ForeignKey('Quizzes.QuizID'), nullable=False)  # QuizID
    question_text = db.Column('QuestionText', UnicodeTextType, nullable=False)  # QuestionText - NVARCHAR(MAX)
    option_a = db.Column('OptionA', UnicodeString(255))  # OptionA - NVARCHAR(255)
    option_b = db.Column('OptionB', UnicodeString(255))  # OptionB - NVARCHAR(255)
    option_c = db.Column('OptionC', UnicodeString(255))  # OptionC - NVARCHAR(255)
    option_d = db.Column('OptionD', UnicodeString(255))  # OptionD - NVARCHAR(255)
    correct_option = db.Column('CorrectOption', db.String(1))  # CorrectOption (A/B/C/D)

    quiz = db.relationship('Quiz', back_populates='questions', foreign_keys=[quiz_id])


class QuizResult(db.Model):
    __tablename__ = 'QuizResults'  # PascalCase for MSSQL
    id = db.Column('ResultID', db.Integer, primary_key=True)  # ResultID
    # Reference quizzes.QuizID to match existing DB
    quiz_id = db.Column('QuizID', db.Integer, db.ForeignKey('Quizzes.QuizID'), nullable=False)  # QuizID
    user_id = db.Column('UserID', db.Integer, db.ForeignKey('Users.UserID'), nullable=False)  # UserID
    score = db.Column('Score', db.Numeric(5, 2), default=0.0)  # Score (decimal(5,2) in DB)
    submitted_at = db.Column('SubmittedAt', db.DateTime, default=datetime.utcnow)  # SubmittedAt

    quiz = db.relationship('Quiz', back_populates='results', foreign_keys=[quiz_id])
    user = db.relationship('User', back_populates='quiz_results', foreign_keys=[user_id])
