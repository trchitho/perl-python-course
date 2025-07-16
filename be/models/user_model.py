from extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')

    department = db.Column(db.String(100))                     # Chỉ giảng viên
    joined_date = db.Column(db.Date, default=datetime.utcnow) # Chỉ giảng viên

    avatar_url = db.Column(db.Text)  # 🆕 Avatar riêng cho mỗi người (sinh viên hoặc giảng viên)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
