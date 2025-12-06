from app import db


class AuditLog(db.Model):
    __tablename__ = 'AuditLogs'  # PascalCase for MSSQL
    id = db.Column('LogID', db.Integer, primary_key=True)  # LogID
    user_id = db.Column('AdminID', db.Integer, db.ForeignKey('Users.UserID'), nullable=False)  # AdminID
    action = db.Column('Action', db.String(100))  # Action
    resource = db.Column('Target', db.String(100))  # Target (mapped to resource in code)
    description = db.Column('Description', db.Text)  # Description
    # success = db.Column(db.Boolean, default=True)  # Not in DB schema - commented out
    created_at = db.Column('Timestamp', db.DateTime, default=db.func.now())  # Timestamp

