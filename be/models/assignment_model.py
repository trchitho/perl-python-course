from extensions import db
from datetime import datetime

class Assignment(db.Model):
    __tablename__ = 'assignments'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    deadline = db.Column(db.DateTime)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    
