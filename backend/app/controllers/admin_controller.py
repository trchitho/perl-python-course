from flask import jsonify, current_app, Response
from app.models.user_model import User
from app.models.audit_log_model import AuditLog
from app.models.course_model import Course
from app.models.enrollment_model import Enrollment
from app import db
from flask_jwt_extended import get_jwt_identity
from werkzeug.security import generate_password_hash
import json
import os

# Helper function for logging admin actions
def _log_admin(action: str, target: str, description: str = ''):
    """Logs an admin action to the AuditLog."""
    try:
        admin_id = int(get_jwt_identity()) if get_jwt_identity() is not None else None
        log = AuditLog(
            user_id=admin_id, 
            action=action, 
            resource=target,
            description=description or f"{action} on {target}"
        )
        db.session.add(log)
        db.session.commit()
        
        # Console logging for QA03: Security - Admin Action Logging
        current_app.logger.info(
            f"📝 ADMIN ACTION LOGGED: Admin {admin_id} performed '{action}' "
            f"on '{target}' - {description}"
        )
    except Exception as e:
        current_app.logger.error(f"Failed to log admin action: {e}")

def list_users():
    """Lists all non-admin users with pagination support."""
    from flask import request
    
    # Get pagination parameters from query string
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Limit per_page to prevent abuse
    per_page = min(per_page, 100)
    
    # Query with pagination
    query = User.query.filter(User.role != 'admin').order_by(User.id.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'users': [{
            'id': u.id,
            'fullname': u.fullname,
            'email': u.email,
            'role': u.role,
        } for u in pagination.items],
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev,
        }
    })

def _get_user_and_check(user_id: int):
    """Fetches a user by ID and ensures they are not an admin."""
    user = User.query.get(user_id)
    if not user:
        return None, jsonify({'error': 'User not found'}), 404
    if user.role == 'admin':
        return None, jsonify({'error': 'Cannot modify an admin account'}), 403
    return user, None, None

def lock_user(user_id: int):
    """Deactivates a user account."""
    # Feature disabled - is_active column not in DB schema
    return jsonify({'error': 'Lock user feature is disabled'}), 501
    
    # user, err_res, err_code = _get_user_and_check(user_id)
    # if err_res:
    #     return err_res, err_code
    # 
    # user.is_active = False
    # _log_admin('lock_user', f'user:{user_id}')
    # db.session.commit()
    # return jsonify({'message': 'User locked'})

def unlock_user(user_id: int):
    """Activates a user account."""
    # Feature disabled - is_active column not in DB schema
    return jsonify({'error': 'Unlock user feature is disabled'}), 501
    
    # user, err_res, err_code = _get_user_and_check(user_id)
    # if err_res:
    #     return err_res, err_code
    #     
    # user.is_active = True
    # _log_admin('unlock_user', f'user:{user_id}')
    # db.session.commit()
    # return jsonify({'message': 'User unlocked'})

def create_user(data):
    """Creates a new user."""
    email = data.get('email')
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400

    new_user = User(
        fullname=data.get('fullname') or 'New User',
        email=email,
        role=data.get('role') or 'student'
    )
    new_user.set_password(data.get('password') or '123456')
    
    db.session.add(new_user)
    _log_admin('create_user', f'user_email:{email}')
    db.session.commit()
    
    return jsonify({'message': 'User created', 'id': new_user.id}), 201

def update_user(user_id: int, data):
    """Updates a user's details (admin cannot change password)."""
    user, err_res, err_code = _get_user_and_check(user_id)
    if err_res:
        return err_res, err_code

    if 'fullname' in data:
        user.fullname = data['fullname']
    if 'email' in data:
        # Ensure new email doesn't already exist
        existing = User.query.filter(User.email == data['email'], User.id != user_id).first()
        if existing:
            return jsonify({'error': 'New email already in use'}), 400
        user.email = data['email']
    # Password change removed - admin cannot change user passwords for security
    
    _log_admin('update_user', f'user:{user_id}')
    db.session.commit()
    return jsonify({'message': 'User updated'})

def delete_user(user_id: int):
    """Deletes a user."""
    user, err_res, err_code = _get_user_and_check(user_id)
    if err_res:
        return err_res, err_code
        
    db.session.delete(user)
    _log_admin('delete_user', f'user:{user_id}')
    db.session.commit()
    return jsonify({'message': 'User deleted'})

def set_role(user_id: int, role: str):
    """Sets a user's role."""
    if role == 'admin':
         return jsonify({'error': 'Cannot assign admin role directly'}), 403

    user, err_res, err_code = _get_user_and_check(user_id)
    if err_res:
        return err_res, err_code

    user.role = role
    _log_admin('set_role', f'user:{user_id}:{role}')
    db.session.commit()
    return jsonify({'message': 'Role updated'})

def admin_stats():
    """Retrieves high-level statistics for the admin dashboard."""
    users = User.query.count()
    courses = Course.query.count()
    enrollments = Enrollment.query.count()
    # errors = AuditLog.query.filter_by(success=False).count()  # success column not in DB
    errors = 0  # Placeholder - success column not in database schema
    return jsonify({
        'users': users, 
        'courses': courses, 
        'enrollments': enrollments,
        'errors': errors
    })

def list_enrollments_admin():
    """Lists all course enrollments with student and course details and pagination."""
    from flask import request
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    per_page = min(per_page, 100)
    
    # Query with pagination
    query = Enrollment.query.options(
        db.joinedload(Enrollment.student),
        db.joinedload(Enrollment.course)
    ).order_by(Enrollment.id.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'enrollments': [{
            'id': e.id,
            'user_id': e.student_id,
            'course_id': e.course_id,
            'status': e.status,
            'payment_status': e.payment_status,
            'student_name': e.student.fullname if e.student else 'N/A',
            'email': e.student.email if e.student else 'N/A',
            'course_name': e.course.name if e.course else 'N/A',
            'enrolled_date': e.enrolled_at.isoformat() if e.enrolled_at else None,
        } for e in pagination.items],
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev,
        }
    })

def approve_enrollment_admin(en_id: int):
    """Approves an enrollment request."""
    enrollment = Enrollment.query.get(en_id)
    if not enrollment:
        return jsonify({'error': 'Enrollment not found'}), 404
        
    enrollment.status = 'approved'
    _log_admin('approve_enrollment', f'enroll:{en_id}')
    db.session.commit()
    return jsonify({'message': 'Enrollment approved'})

def reject_enrollment_admin(en_id: int):
    """Rejects an enrollment request."""
    enrollment = Enrollment.query.get(en_id)
    if not enrollment:
        return jsonify({'error': 'Enrollment not found'}), 404
        
    enrollment.status = 'rejected'
    _log_admin('reject_enrollment', f'enroll:{en_id}')
    db.session.commit()
    return jsonify({'message': 'Enrollment rejected'})

def list_logs():
    """Lists the last 500 audit logs."""
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(500).all()
    return jsonify([{
        'id': l.id,
        'user_id': l.user_id,
        'action': l.action,
        'resource': l.resource,
        'description': l.description,
        'created_at': l.created_at.isoformat() if l.created_at else ''
    } for l in logs])

def export_logs(file_format: str):
    """Exports all audit logs to a CSV file."""
    if file_format != 'csv':
        return Response("Only CSV export is currently supported.", mimetype='text/plain', status=400)

    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).all()
    # Using a generator to avoid loading all data into memory at once for large exports
    def generate():
        yield 'id,user_id,action,resource,success,created_at\n'
        for l in logs:
            resource = (l.resource or '').replace(',', ' ')
            created_at = l.created_at or ''
            success = 1 if l.success else 0
            yield f"{l.id},{l.user_id or ''},{l.action or ''},{resource},{success},{created_at}\n"
    
    headers = {'Content-Disposition': 'attachment; filename=audit_logs.csv'}
    return Response(generate(), mimetype='text/csv', headers=headers)

# The following functions for settings, backup etc. are file-system or placeholders
# and do not use the database dialect switcher. They can remain as they are.
_SETTINGS_FILE = os.path.join(os.path.dirname(__file__), '..', 'static', 'settings.json')

def _read_settings():
    try:
        with open(_SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def _write_settings(data: dict):
    os.makedirs(os.path.dirname(_SETTINGS_FILE), exist_ok=True)
    with open(_SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_settings():
    return jsonify(_read_settings())

def update_settings(data):
    cfg = _read_settings()
    cfg.update({
        'smtp_host': data.get('smtp_host'),
        'smtp_port': data.get('smtp_port'),
        'smtp_user': data.get('smtp_user'),
        'ai_key': data.get('ai_key'),
        'upload_limit_mb': data.get('upload_limit_mb'),
    })
    _write_settings(cfg)
    _log_admin('update_settings', 'system')
    db.session.commit()
    return jsonify({'message': 'Settings saved'})

def run_backup_job():
    _log_admin('backup', 'database')
    db.session.commit()
    return jsonify({'message': 'Backup job started'})

def list_courses_admin():
    """Admin lists all courses with teacher info and enrollment count"""
    courses = Course.query.options(
        db.joinedload(Course.teacher)
    ).order_by(Course.id.desc()).all()
    
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'description': c.description,
        'category': c.category,
        'duration': c.duration,
        'status': c.status,
        'teacher_id': c.teacher_id,
        'teacher_name': c.teacher.fullname if c.teacher else 'N/A',
        'enrollment_count': Enrollment.query.filter_by(course_id=c.id).count(),
        'created_at': c.created_at.isoformat() if c.created_at else None,
    } for c in courses])

def delete_course_admin(course_id: int):
    """Admin deletes a course"""
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    
    db.session.delete(course)
    _log_admin('delete_course', f'course:{course_id}')
    db.session.commit()
    return jsonify({'message': 'Course deleted'})

def update_course_admin(course_id: int, data):
    """Admin updates a course"""
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    
    if 'name' in data:
        course.name = data['name']
    if 'description' in data:
        course.description = data['description']
    if 'category' in data:
        course.category = data['category']
    if 'duration' in data:
        course.duration = data['duration']
    if 'status' in data:
        course.status = data['status']
    
    _log_admin('update_course', f'course:{course_id}')
    db.session.commit()
    return jsonify({'message': 'Course updated'})
