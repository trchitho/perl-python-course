from datetime import datetime
from app import db


class Enrollment(db.Model):
    __tablename__ = 'Enrollments'  # PascalCase for MSSQL
    id = db.Column('EnrollmentID', db.Integer, primary_key=True)  # EnrollmentID
    student_id = db.Column('UserID', db.Integer, db.ForeignKey('Users.UserID'), nullable=False)  # UserID (not StudentID!)
    course_id = db.Column('CourseID', db.Integer, db.ForeignKey('Courses.CourseID'), nullable=False)  # CourseID
    status = db.Column('Status', db.String(20), default='pending')  # Status (pending/approved/rejected)
    payment_status = db.Column('PaymentStatus', db.String(20), default='unpaid')  # PaymentStatus
    enrolled_at = db.Column('EnrolledDate', db.DateTime, default=datetime.utcnow)  # EnrolledDate

    student = db.relationship('User', back_populates='enrollments', foreign_keys=[student_id])
    course = db.relationship('Course', back_populates='enrollments', foreign_keys=[course_id])
