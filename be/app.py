from flask_cors import CORS
from flask import Flask
from config import Config
from extensions import db, jwt
from routes.auth_routes import auth_bp
from routes.teacher_routes import teacher_bp
from routes.student_routes import student_bp
from routes.judge_routes import judge_bp
from routes.ai_route import ai_bp



def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    #CORS(app)
    #CORS(app, resources={r"/api/*": {"origins": "http://127.0.0.1:5500"}}, supports_credentials=True)
    #CORS(app, origins=["http://127.0.0.1:5500"], supports_credentials=True)
    CORS(app, supports_credentials=True)

    CORS(app, resources={r"/api/*": {"origins": [
    "http://localhost:5501",
    "http://127.0.0.1:5501"
]}}, supports_credentials=True)

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(teacher_bp, url_prefix='/api/teacher')
    app.register_blueprint(student_bp, url_prefix='/api/student')
    app.register_blueprint(judge_bp, url_prefix="/api/judge")
    app.register_blueprint(ai_bp)



    # ✅ Định nghĩa route home tại đây
    @app.route('/')
    def home():
        return "Flask backend is running successfully!"

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)
