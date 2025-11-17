from datetime import datetime
from app import db


class Quiz(db.Model):
    __tablename__ = 'quizzes'
    # Match existing SQL Server schema where PK column is QuizID
    id = db.Column('QuizID', db.Integer, primary_key=True)  # QuizID
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)  # CourseID
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'))  # LessonID
    title = db.Column(db.String(200), nullable=False)  # Title
    description = db.Column(db.Text)  # Description
    total_questions = db.Column(db.Integer, default=0)  # TotalQuestions
    time_limit = db.Column(db.Integer)  # TimeLimit (minutes)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # CreatedAt


class QuizQuestion(db.Model):
    __tablename__ = 'quiz_questions'
    id = db.Column(db.Integer, primary_key=True)  # QuestionID
    # Reference quizzes.QuizID to match existing DB
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.QuizID'), nullable=False)  # QuizID
    question_text = db.Column(db.Text, nullable=False)  # QuestionText
    option_a = db.Column(db.Text)
    option_b = db.Column(db.Text)
    option_c = db.Column(db.Text)
    option_d = db.Column(db.Text)
    correct_option = db.Column(db.String(1))  # A/B/C/D


class QuizResult(db.Model):
    __tablename__ = 'quiz_results'
    id = db.Column(db.Integer, primary_key=True)  # ResultID
    # Reference quizzes.QuizID to match existing DB
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.QuizID'), nullable=False)  # QuizID
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # UserID
    score = db.Column(db.Float, default=0.0)  # Score
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)  # SubmittedAt
