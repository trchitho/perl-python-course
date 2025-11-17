from datetime import datetime
from app import db


class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    id = db.Column(db.Integer, primary_key=True)  # EnrollmentID
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # UserID
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)  # CourseID
    status = db.Column(db.String(30), default='active')  # Status
    payment_status = db.Column(db.String(30), default='paid')  # PaymentStatus
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)  # EnrolledDate
