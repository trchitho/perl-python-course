from datetime import datetime
from app import db


class PlacementTest(db.Model):
    __tablename__ = 'PlacementTests'  # PascalCase for MSSQL
    id = db.Column('TestID', db.Integer, primary_key=True)  # TestID
    user_id = db.Column('UserID', db.Integer, db.ForeignKey('Users.UserID'), nullable=False)  # UserID
    score = db.Column('Score', db.Numeric(5, 2), default=0.0)  # Score (decimal(5,2) in DB)
    recommended_level = db.Column('RecommendedLevel', db.String(50))  # RecommendedLevel
    taken_at = db.Column('TakenAt', db.DateTime, default=datetime.utcnow)  # TakenAt

