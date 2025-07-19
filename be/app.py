from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from config import Config
from extensions import db, jwt
from routes.auth_routes import auth_bp
from routes.teacher_routes import teacher_bp
from routes.student_routes import student_bp
from routes.judge_routes import judge_bp
from routes.ai_route import ai_bp
import os


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["UPLOAD_FOLDER"] = os.path.join(os.getcwd(), "uploads")
    

    # Cấu hình CORS
    CORS(app, supports_credentials=True, resources={
        r"/api/*": {
            "origins": ["http://127.0.0.1:5500", "http://localhost:5500"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Khởi tạo extensions
    db.init_app(app)
    jwt.init_app(app)

    # Cấu hình thư mục upload
    UPLOAD_FOLDER = 'uploads'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Đăng ký blueprint (1 lần duy nhất mỗi loại)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(teacher_bp, url_prefix='/api/teacher')
    app.register_blueprint(student_bp, url_prefix='/api/student')
    app.register_blueprint(judge_bp, url_prefix='/api/judge')
    app.register_blueprint(ai_bp)

    # Route phục vụ ảnh upload
    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        upload_folder = app.config.get("UPLOAD_FOLDER", "uploads")
        return send_from_directory(upload_folder, filename)

    # Route test
    @app.route('/')
    def home():
        return "Flask backend is running successfully!"

    return app


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)
