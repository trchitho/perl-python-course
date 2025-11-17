from datetime import datetime
from app import db


class PlacementTest(db.Model):
    __tablename__ = 'placement_tests'
    id = db.Column(db.Integer, primary_key=True)  # TestID
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # UserID
    score = db.Column(db.Float, default=0.0)  # Score
    recommended_level = db.Column(db.String(20))  # RecommendedLevel
    taken_at = db.Column(db.DateTime, default=datetime.utcnow)  # TakenAt

