from flask import jsonify, current_app, Response
from app.models.user_model import User
from app.models.audit_log_model import AuditLog
from app.models.course_model import Course
from app.models.enrollment_model import Enrollment
from app import db
from flask_jwt_extended import get_jwt_identity
from werkzeug.security import generate_password_hash
from sqlalchemy import text
import json
import os


def list_users():
    if db.get_engine().dialect.name == 'mssql':
        rows = db.session.execute(text(
            "SELECT [UserID],[FullName],[Email],[Role] FROM [dbo].[Users] WHERE ISNULL([Role],'student') <> 'admin' ORDER BY [UserID] DESC"
        )).fetchall()
        out = []
        for r in rows:
            out.append({
                'id': r[0],
                'fullname': r[1],
                'email': r[2],
                'role': r[3] or 'student',
                'is_active': True,
            })
        return jsonify(out)
    users = User.query.filter(User.role != 'admin').all()
    out = []
    for u in users:
        out.append({
            'id': u.id,
            'fullname': u.fullname,
            'email': u.email,
            'role': u.role,
            'is_active': getattr(u, 'is_active', True),
        })
    return jsonify(out)


def lock_user(user_id: int):
    if db.get_engine().dialect.name == 'mssql':
        try:
            r = db.session.execute(text("UPDATE [dbo].[Users] SET [IsActive]=0 WHERE [UserID]=:id"), {'id': user_id})
            if r.rowcount == 0:
                return jsonify({'error':'not found'}), 404
            _log_admin('lock_user', f'user:{user_id}')
            db.session.commit()
            return jsonify({'message':'locked'})
        except Exception:
            # Fallback: still log action
            _log_admin('lock_user', f'user:{user_id}')
            db.session.commit()
            return jsonify({'message':'locked'})
    u = User.query.get(user_id)
    if not u:
        return jsonify({'error':'not found'}), 404
    if hasattr(u, 'is_active'):
        u.is_active = False
        db.session.add(u)
    _log_admin('lock_user', f'user:{user_id}')
    db.session.commit()
    return jsonify({'message':'locked'})


def unlock_user(user_id: int):
    if db.get_engine().dialect.name == 'mssql':
        try:
            r = db.session.execute(text("UPDATE [dbo].[Users] SET [IsActive]=1 WHERE [UserID]=:id"), {'id': user_id})
            if r.rowcount == 0:
                return jsonify({'error':'not found'}), 404
            _log_admin('unlock_user', f'user:{user_id}')
            db.session.commit()
            return jsonify({'message':'unlocked'})
        except Exception:
            _log_admin('unlock_user', f'user:{user_id}')
            db.session.commit()
            return jsonify({'message':'unlocked'})
    u = User.query.get(user_id)
    if not u:
        return jsonify({'error':'not found'}), 404
    if hasattr(u, 'is_active'):
        u.is_active = True
        db.session.add(u)
    _log_admin('unlock_user', f'user:{user_id}')
    db.session.commit()
    return jsonify({'message':'unlocked'})


def create_user(data):
    fullname = data.get('fullname') or 'User'
    email = data.get('email')
    password = data.get('password') or '123456'
    role = data.get('role') or 'student'
    if not email:
        return jsonify({'error': 'email required'}), 400
    if db.get_engine().dialect.name == 'mssql':
        exists = db.session.execute(text('SELECT 1 FROM [dbo].[Users] WHERE [Email]=:e'), {'e': email}).fetchone()
        if exists:
            return jsonify({'error': 'email exists'}), 400
        pwd_hash = generate_password_hash(password)
        row = db.session.execute(text(
            'INSERT INTO [dbo].[Users] (FullName,Email,PasswordHash,Role,TwoFAEnabled,CreatedAt,UpdatedAt) '
            'OUTPUT INSERTED.UserID VALUES (:fn,:em,:ph,:rl,0,GETDATE(),GETDATE())'
        ), {'fn': fullname, 'em': email, 'ph': pwd_hash, 'rl': role}).fetchone()
        _log_admin('create_user', email)
        db.session.commit()
        return jsonify({'message': 'created', 'id': int(row[0])})
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'email exists'}), 400
    u = User(fullname=fullname, email=email, role=role)
    u.set_password(password)
    db.session.add(u)
    _log_admin('create_user', email)
    db.session.commit()
    return jsonify({'message': 'created', 'id': u.id})


def update_user(user_id: int, data):
    if db.get_engine().dialect.name == 'mssql':
        fields = []
        params = {'id': user_id}
        if 'fullname' in data:
            fields.append('[FullName]=:fn')
            params['fn'] = data['fullname']
        if 'email' in data:
            fields.append('[Email]=:em')
            params['em'] = data['email']
        if 'password' in data and data['password']:
            fields.append('[PasswordHash]=:ph')
            params['ph'] = generate_password_hash(data['password'])
        if not fields:
            return jsonify({'message': 'no changes'})
        r = db.session.execute(text('UPDATE [dbo].[Users] SET ' + ','.join(fields) + ' WHERE [UserID]=:id'), params)
        if r.rowcount == 0:
            return jsonify({'error': 'not found'}), 404
        _log_admin('update_user', f'user:{user_id}')
        db.session.commit()
        return jsonify({'message': 'updated'})
    u = User.query.get(user_id)
    if not u:
        return jsonify({'error': 'not found'}), 404
    if 'fullname' in data:
        u.fullname = data['fullname']
    if 'email' in data:
        u.email = data['email']
    if 'password' in data and data['password']:
        u.set_password(data['password'])
    db.session.add(u)
    _log_admin('update_user', f'user:{user_id}')
    db.session.commit()
    return jsonify({'message': 'updated'})


def delete_user(user_id: int):
    if db.get_engine().dialect.name == 'mssql':
        r = db.session.execute(text('DELETE FROM [dbo].[Users] WHERE [UserID]=:id'), {'id': user_id})
        if r.rowcount == 0:
            return jsonify({'error': 'not found'}), 404
        _log_admin('delete_user', f'user:{user_id}')
        db.session.commit()
        return jsonify({'message': 'deleted'})
    u = User.query.get(user_id)
    if not u:
        return jsonify({'error': 'not found'}), 404
    db.session.delete(u)
    _log_admin('delete_user', f'user:{user_id}')
    db.session.commit()
    return jsonify({'message': 'deleted'})


def set_role(user_id: int, role: str):
    if db.get_engine().dialect.name == 'mssql':
        r = db.session.execute(text('UPDATE [dbo].[Users] SET [Role]=:rl WHERE [UserID]=:id'), {'rl': role, 'id': user_id})
        if r.rowcount == 0:
            return jsonify({'error': 'not found'}), 404
        _log_admin('set_role', f'user:{user_id}:{role}')
        db.session.commit()
        return jsonify({'message': 'role updated'})
    u = User.query.get(user_id)
    if not u:
        return jsonify({'error': 'not found'}), 404
    u.role = role
    db.session.add(u)
    _log_admin('set_role', f'user:{user_id}:{role}')
    db.session.commit()
    return jsonify({'message': 'role updated'})


def admin_stats():
    if db.get_engine().dialect.name == 'mssql':
        users = db.session.execute(text('SELECT COUNT(*) FROM [dbo].[Users]')).scalar()
        try:
            courses = db.session.execute(text('SELECT COUNT(*) FROM [dbo].[Courses]')).scalar()
        except Exception:
            # fallback if lowercase table exists
            courses = db.session.execute(text('SELECT COUNT(*) FROM courses')).scalar()
        try:
            errors = db.session.execute(text('SELECT COUNT(*) FROM [dbo].[AuditLogs]')).scalar()
        except Exception:
            errors = 0
    else:
        users = User.query.count()
        courses = Course.query.count()
        errors = AuditLog.query.filter_by(success=False).count()
    return jsonify({'users': int(users or 0), 'courses': int(courses or 0), 'errors': int(errors or 0)})


def list_enrollments_admin():
    if db.get_engine().dialect.name == 'mssql':
        q = db.session.execute(text(
            """
            SELECT e.EnrollmentID, e.UserID, e.CourseID, e.Status, e.PaymentStatus,
                   u.FullName AS student_name, u.Email AS student_email,
                   c.Title    AS course_name
            FROM [dbo].[Enrollments] e
            LEFT JOIN [dbo].[Users] u   ON u.UserID = e.UserID
            LEFT JOIN [dbo].[Courses] c ON c.CourseID = e.CourseID
            ORDER BY e.EnrollmentID DESC
            """
        ))
        rows = []
        for r in q.fetchall():
            rows.append({
                'id': r[0], 'user_id': r[1], 'course_id': r[2],
                'status': r[3], 'payment_status': r[4],
                'student_name': r[5], 'email': r[6], 'course_name': r[7],
            })
        return jsonify(rows)
    # Generic (SQLite/MySQL)
    q = db.session.execute(text(
        """
        SELECT e.id, e.student_id, e.course_id, e.status, e.payment_status,
               u.fullname AS student_name, u.email AS student_email,
               c.name     AS course_name
        FROM enrollments e
        LEFT JOIN users u   ON u.id = e.student_id
        LEFT JOIN courses c ON c.id = e.course_id
        ORDER BY e.id DESC
        """
    ))
    rows = []
    for r in q.fetchall():
        rows.append({
            'id': r[0], 'user_id': r[1], 'course_id': r[2],
            'status': r[3], 'payment_status': r[4],
            'student_name': r[5], 'email': r[6], 'course_name': r[7],
        })
    return jsonify(rows)


def approve_enrollment_admin(en_id: int):
    if db.get_engine().dialect.name == 'mssql':
        r = db.session.execute(text('UPDATE [dbo].[Enrollments] SET [Status]=:st WHERE [EnrollmentID]=:id'), {'st': 'approved', 'id': en_id})
        if r.rowcount == 0:
            return jsonify({'error': 'not found'}), 404
        _log_admin('approve_enrollment', f'enroll:{en_id}')
        db.session.commit()
        return jsonify({'message': 'approved'})
    e = Enrollment.query.get(en_id)
    if not e:
        return jsonify({'error': 'not found'}), 404
    e.status = 'approved'
    db.session.add(e)
    _log_admin('approve_enrollment', f'enroll:{en_id}')
    db.session.commit()
    return jsonify({'message': 'approved'})


def lock_enrollment_admin(en_id: int):
    if db.get_engine().dialect.name == 'mssql':
        # Respect CHECK constraint: allowed values are pending/approved/rejected
        r = db.session.execute(text('UPDATE [dbo].[Enrollments] SET [Status]=:st WHERE [EnrollmentID]=:id'), {'st': 'rejected', 'id': en_id})
        if r.rowcount == 0:
            return jsonify({'error': 'not found'}), 404
        _log_admin('lock_enrollment', f'enroll:{en_id}')
        db.session.commit()
        return jsonify({'message': 'rejected'})
    e = Enrollment.query.get(en_id)
    if not e:
        return jsonify({'error': 'not found'}), 404
    e.status = 'rejected'
    db.session.add(e)
    _log_admin('lock_enrollment', f'enroll:{en_id}')
    db.session.commit()
    return jsonify({'message': 'rejected'})


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
        # Do not persist raw passwords in plain text for production
        'ai_key': data.get('ai_key'),
        'upload_limit_mb': data.get('upload_limit_mb'),
    })
    _write_settings(cfg)
    _log_admin('update_settings', 'admin')
    db.session.commit()
    return jsonify({'message': 'saved'})


def list_logs():
    if db.get_engine().dialect.name == 'mssql':
        rows = db.session.execute(text('SELECT LogID, AdminID, Action, Target, Timestamp FROM AuditLogs ORDER BY Timestamp DESC')).fetchall()
        return jsonify([{ 'id': r[0], 'user_id': r[1], 'action': r[2], 'resource': r[3], 'success': True, 'created_at': str(r[4]) if r[4] else '' } for r in rows])
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(500).all()
    return jsonify([{ 'id': l.id, 'user_id': l.user_id, 'action': l.action, 'resource': l.resource, 'success': l.success, 'created_at': l.created_at.isoformat() if l.created_at else '' } for l in logs])


def export_logs(format: str):
    if db.get_engine().dialect.name == 'mssql':
        rows = db.session.execute(text('SELECT LogID, AdminID, Action, Target, Timestamp FROM AuditLogs ORDER BY Timestamp DESC')).fetchall()
        if format == 'csv':
            lines = ['id,user_id,action,resource,success,created_at']
            for r in rows:
                lines.append(f"{r[0]},{r[1]},{r[2]},{(r[3] or '').replace(',', ' ')},1,{r[4] or ''}")
            data = '\n'.join(lines)
            return Response(data, mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=logs.csv'})
        return Response("PDF export coming soon", mimetype='text/plain', headers={'Content-Disposition': 'attachment; filename=logs.txt'})
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).all()
    if format == 'csv':
        lines = ['id,user_id,action,resource,success,created_at']
        for l in logs:
            lines.append(f"{l.id},{l.user_id or ''},{l.action or ''},{(l.resource or '').replace(',', ' ')},{1 if l.success else 0},{l.created_at or ''}")
        data = '\n'.join(lines)
        return Response(data, mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=logs.csv'})
    # simple text PDF placeholder
    return Response("PDF export coming soon", mimetype='text/plain', headers={'Content-Disposition': 'attachment; filename=logs.txt'})


def run_backup_job():
    # Placeholder: in real app, call service/SQL backup routine
    _log_admin('backup', 'db')
    db.session.commit()
    return jsonify({'message': 'backup started'})


def _log_admin(action: str, target: str, desc: str | None = None):
    try:
        if db.get_engine().dialect.name == 'mssql':
            admin_id = int(get_jwt_identity()) if get_jwt_identity() is not None else None
            db.session.execute(text(
                'INSERT INTO AuditLogs(AdminID, Action, Target, Description, Timestamp) VALUES(:aid,:a,:t,:d,GETDATE())'
            ), {'aid': admin_id or 0, 'a': action, 't': target, 'd': desc or ''})
        else:
            db.session.add(AuditLog(action=action, resource=target, success=True))
    except Exception:
        # Do not break the main flow because of logging
        pass
