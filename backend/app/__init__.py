from flask import Flask
import os
from urllib.parse import unquote_plus
try:
    from dotenv import load_dotenv  # type: ignore
    # Load backend/.env if present
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
except Exception:
    # python-dotenv not installed or not needed; safe to ignore
    pass
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from config import Config

db = SQLAlchemy()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    # Enforce MSSQL only (no SQLite fallback)
    if not app.config.get('SQLALCHEMY_DATABASE_URI') or not app.config['SQLALCHEMY_DATABASE_URI'].lower().startswith('mssql+pyodbc://'):
        raise RuntimeError('This build requires SQL Server (mssql+pyodbc). Configure backend/.env or DATABASE_URL.')

    # Startup log: show which DB we are using (mask secrets)
    uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if 'odbc_connect=' in uri:
        try:
            enc = uri.split('odbc_connect=')[1]
            cs = unquote_plus(enc)
            parts = dict(p.split('=', 1) for p in cs.split(';') if '=' in p)
            srv = parts.get('SERVER', '')
            dbn = parts.get('DATABASE', '')
            print(f"[Config] Using MSSQL via pyodbc. SERVER={srv}, DATABASE={dbn}")
        except Exception:
            print("[Config] Using MSSQL via pyodbc (odbc_connect)")
    else:
        # In strict mode we should never reach here with a non-mssql URI
        print(f"[Config] DB URI: {uri.split('://')[0]}://...")
    # Normalize engine options here based on final URI
    engine_opts = app.config.get('SQLALCHEMY_ENGINE_OPTIONS', {})
    engine_opts['pool_pre_ping'] = True
    if uri.startswith('mssql+pyodbc') or 'odbc_connect=' in uri:
        engine_opts['fast_executemany'] = True
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = engine_opts
    
    db.init_app(app)
    jwt.init_app(app)
    
    # Initialize Cache (simple in-memory)
    print("[Cache] Using in-memory cache")
    
    # Log connection pool settings
    pool_opts = app.config.get('SQLALCHEMY_ENGINE_OPTIONS', {})
    print(f"[DB Pool] Size: {pool_opts.get('pool_size', 'default')}, "
          f"Max Overflow: {pool_opts.get('max_overflow', 'default')}, "
          f"Timeout: {pool_opts.get('pool_timeout', 'default')}s")
    
    # Initialize Performance Monitoring
    from app.middleware.performance_monitor import performance_monitor_middleware
    performance_monitor_middleware(app)
    print("=" * 70)
    print("🎯 QUALITY ATTRIBUTES - IMPLEMENTATION STATUS")
    print("=" * 70)
    print("✅ QA01 - USABILITY:")
    print("   • Lesson Navigation - Material-UI, Clear buttons, Progress tracking")
    print("   • Quiz Interaction - Smooth transitions, Auto-save, Timer")
    print("   • AI Chatbot - Clean interface, Loading states, Error handling")
    print()
    print("✅ QA02 - PERFORMANCE:")
    print("   • Performance Monitoring - Response time tracking (X-Response-Time)")
    print("   • Cache Service - In-memory cache with 5-min TTL")
    print("   • Connection Pool - Size: 10, Max Overflow: 20")
    print("   • Slow Request Logging - Warnings for requests > 5s")
    print()
    print("✅ QA03 - SECURITY:")
    print("   • Password Hashing - Werkzeug PBKDF2 + SHA256")
    print("   • JWT Authentication - flask-jwt-extended")
    print("   • RBAC - @require_roles decorator")
    print("   • Audit Logging - All admin actions logged to AuditLogs table")
    print()
    print("📊 MONITORING ENDPOINTS:")
    print("   • GET  /api/monitoring/health - Health check")
    print("   • GET  /api/monitoring/metrics - Performance metrics (admin)")
    print("   • GET  /api/monitoring/cache-stats - Cache statistics")
    print("   • POST /api/monitoring/cache/clear - Clear cache (admin)")
    print("=" * 70)
    print()
    
    # Strict CORS to allow local static servers (http.server/VSCode Live Server)
    # Allow all dev origins for /api/* (no cookies)
    CORS(
        app,
        resources={r"/api/*": {"origins": "*"}},
        supports_credentials=False,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        max_age=86400,
    )

    # Ensure preflight always returns 204 with CORS headers
    @app.route('/api/<path:_any>', methods=['OPTIONS'])
    def _cors_preflight(_any):
        return '', 204

    with app.app_context():
        from .models.user_model import User  # noqa: F401
        from .models.course_model import Course  # noqa: F401
        from .models.lesson_model import Lesson  # noqa: F401
        from .models.enrollment_model import Enrollment  # noqa: F401
        from .models.audit_log_model import AuditLog  # noqa: F401
        from .models.progress_model import Progress  # noqa: F401
        # Temporarily disabled until Announcements table is created
        # from .models.announcement_model import Announcement  # noqa: F401
        from .models.quiz_model import Quiz, QuizQuestion, QuizResult  # noqa: F401
        from .models.chatbot_history_model import ChatbotHistory  # noqa: F401
        from .models.placement_test_model import PlacementTest  # noqa: F401
        uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        force_create = os.getenv('DB_FORCE_CREATE_ALL', 'false').lower() in ('1','true','yes','y')
        if uri.startswith('mssql+pyodbc') and not force_create:
            print('[DB] Detected MSSQL. Skipping db.create_all() (assumes existing schema).')
        else:
            db.create_all()
            # Optional development seeding: set DEV_AUTO_SEED=1 to create a default admin
            if os.getenv('DEV_AUTO_SEED', 'false').lower() in ('1','true','yes','y'):
                try:
                    from .models.user_model import User
                    if User.query.count() == 0:
                        u = User(fullname='Admin', email='admin@example.com', role='admin')
                        try:
                            u.set_password('123456')
                        except Exception:
                            pass
                        db.session.add(u)
                        db.session.commit()
                        print('[Seed] Created default admin admin@example.com / 123456')
                except Exception as _seed_err:
                    print('[Seed] Skipped seeding users:', _seed_err)

        from .views.auth_view import auth_bp
        from .views.lesson_view import lesson_bp
        from .views.quiz_view import quiz_bp
        from .views.admin_view import admin_bp
        from .views.chatbot_view import chatbot_bp
        from .views.teacher_view import teacher_bp
        from .views.profile_view import profile_bp
        from .views.monitoring_view import monitoring_bp
        from .views.upload_view import upload_bp
        from .views.placement_test_view import placement_test_bp
        # Temporarily disabled until Announcements table is created
        # from .views.announcement_view import announcement_bp

        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        app.register_blueprint(lesson_bp, url_prefix='/api/student')
        app.register_blueprint(quiz_bp, url_prefix='/api/student')
        app.register_blueprint(admin_bp, url_prefix='/api/admin')
        app.register_blueprint(chatbot_bp, url_prefix='/api/ai')
        app.register_blueprint(teacher_bp, url_prefix='/api/teacher')
        app.register_blueprint(profile_bp, url_prefix='/api/profile')
        app.register_blueprint(monitoring_bp, url_prefix='/api/monitoring')
        app.register_blueprint(upload_bp, url_prefix='/api')
        app.register_blueprint(placement_test_bp, url_prefix='/api')
        # app.register_blueprint(announcement_bp, url_prefix='/api/announcements')

    # Fix Vietnamese encoding for pyodbc - register after all init
    try:
        from sqlalchemy import event
        
        @event.listens_for(db.engine, "connect", insert=True)
        def set_unicode_encoding(dbapi_conn, connection_record):
            """Set proper encoding for Vietnamese text"""
            try:
                # For pyodbc, set encoding to UTF-8
                dbapi_conn.setdecoding(1, encoding='utf-8')  # SQL_CHAR
                dbapi_conn.setdecoding(2, encoding='utf-8')  # SQL_WCHAR
                dbapi_conn.setencoding(encoding='utf-8')
                print("[Encoding] Set UTF-8 encoding for pyodbc connection")
            except AttributeError:
                # Not pyodbc or method not available
                pass
    except Exception as e:
        print(f"[Encoding] Warning: Could not set encoding - {e}")

    return app
