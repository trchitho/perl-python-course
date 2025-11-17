from datetime import datetime
from app import db


class Announcement(db.Model):
    __tablename__ = 'announcements'
    id = db.Column(db.Integer, primary_key=True)  # AnnouncementID
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))  # CourseID
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # TeacherID
    title = db.Column(db.String(200))  # Title
    message = db.Column(db.Text, nullable=False)  # Message
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # CreatedAt
