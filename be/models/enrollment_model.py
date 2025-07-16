from extensions import db
from datetime import datetime
from models.user_model import User
from models.course_model import Course

# Enrollment: Mối quan hệ giữa sinh viên và khóa học
class Enrollment(db.Model):
    __tablename__ = 'enrollments'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=db.func.now())

    student = db.relationship('User', backref='enrollments', foreign_keys=[student_id])
    course = db.relationship('Course', backref='enrollments', foreign_keys=[course_id])