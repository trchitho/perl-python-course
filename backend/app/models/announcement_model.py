from datetime import datetime
from app import db


class Announcement(db.Model):
    __tablename__ = 'Announcements'
    
    id = db.Column('AnnouncementID', db.Integer, primary_key=True)
    course_id = db.Column('CourseID', db.Integer, db.ForeignKey('Courses.CourseID'), nullable=True)
    title = db.Column('Title', db.String(200), nullable=False)
    content = db.Column('Content', db.Text, nullable=False)
    created_by = db.Column('CreatedBy', db.Integer, db.ForeignKey('Users.UserID'), nullable=False)
    created_at = db.Column('CreatedAt', db.DateTime, default=datetime.utcnow)
    is_active = db.Column('IsActive', db.Boolean, default=True)
    priority = db.Column('Priority', db.String(20), default='normal')  # low, normal, high, urgent
    
    # Relationships - use foreign_keys to avoid ambiguity
    course = db.relationship('Course', foreign_keys=[course_id], backref='announcements')
    creator = db.relationship('User', foreign_keys=[created_by])
