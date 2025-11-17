from app import db


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    action = db.Column(db.String(100))
    resource = db.Column(db.Text)
    success = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.now())

