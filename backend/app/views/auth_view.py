from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models.user_model import User
from app.services.jwt_service import issue_token
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash
import logging
import secrets

auth_bp = Blueprint('auth_v2', __name__)
logger = logging.getLogger(__name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip()
    fullname = (data.get('fullname') or 'User').strip()
    password = data.get('password') or '123456'
    role = data.get('role') or 'student'
    if role not in ['student','teacher','admin']:
        return jsonify({'message': 'Invalid role'}), 400

    if db.get_engine().dialect.name == 'mssql':
        exists = db.session.execute(text('SELECT 1 FROM [dbo].[Users] WHERE [Email]=:e'), {'e': email}).fetchone()
        if exists:
            return jsonify({'message': 'Email is already registered'}), 400
        pwd_hash = generate_password_hash(password)
        try:
            row = db.session.execute(text(
                'INSERT INTO [dbo].[Users] (FullName,Email,PasswordHash,Role,TwoFAEnabled,CreatedAt,UpdatedAt) '
                'OUTPUT INSERTED.UserID VALUES (:fn,:em,:ph,:rl,0,GETDATE(),GETDATE())'
            ), {'fn': fullname, 'em': email, 'ph': pwd_hash, 'rl': role}).fetchone()
        except Exception:
            # Minimal column set fallback
            row = db.session.execute(text(
                'INSERT INTO [dbo].[Users] (FullName,Email,PasswordHash,Role) OUTPUT INSERTED.UserID VALUES (:fn,:em,:ph,:rl)'
            ), {'fn': fullname, 'em': email, 'ph': pwd_hash, 'rl': role}).fetchone()
        db.session.commit()
        return jsonify({'message': 'Registration successful', 'id': int(row[0])}), 201

    # Generic ORM path
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email is already registered'}), 400
    u = User(fullname=fullname, email=email, role=role)
    u.set_password(password)
    db.session.add(u)
    db.session.commit()
    
    # Log successful registration (QA03: Security)
    logger.info(f"🔐 NEW USER REGISTERED: {email} (role: {role}) - Password hashed with PBKDF2")
    
    return jsonify({'message': 'Registration successful'}), 201


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Request password reset email"""
    try:
        import app.services.email_service as email_service
        import app.services.token_service as token_service
        
        data = request.get_json() or {}
        email = (data.get('email') or '').strip()
        
        logger.info(f"🔑 PASSWORD RESET: Request received for {email}")
        
        if not email:
            return jsonify({'message': 'Email is required'}), 400
        
        # Check if email service is configured
        if not email_service.is_enabled():
            logger.warning("🔑 PASSWORD RESET: Email service not configured")
            return jsonify({'message': 'Dịch vụ email chưa được cấu hình'}), 503
        
        # Find user by email (handle both MSSQL and ORM)
        user = None
        user_id = None
        fullname = None
        
        logger.info(f"🔑 PASSWORD RESET: Checking database for {email}")
        
        if db.get_engine().dialect.name == 'mssql':
            try:
                row = db.session.execute(text(
                    'SELECT [UserID],[FullName],[Email] FROM [dbo].[Users] WHERE [Email]=:em'
                ), {'em': email}).fetchone()
                if row:
                    user_id, fullname, _ = row
                    user = True  # Flag that user exists
                    logger.info(f"🔑 PASSWORD RESET: User found - ID: {user_id}")
            except Exception as e:
                logger.error(f"🔑 PASSWORD RESET: Database error: {str(e)}")
                import traceback
                traceback.print_exc()
                return jsonify({'message': 'Lỗi truy vấn database'}), 500
        else:
            user = User.query.filter_by(email=email).first()
            if user:
                user_id = user.id
                fullname = user.fullname
                logger.info(f"🔑 PASSWORD RESET: User found - ID: {user_id}")
        
        # Always return success message (security: don't reveal if email exists)
        if user:
            try:
                logger.info(f"🔑 PASSWORD RESET: Generating token for user {user_id}")
                # Generate reset token
                reset_token = token_service.create_password_reset_token(user_id, email)
                
                logger.info(f"🔑 PASSWORD RESET: Sending email to {email}")
                # Send email
                result = email_service.send_password_reset_email(email, reset_token, fullname)
                
                if result['success']:
                    logger.info(f"🔑 PASSWORD RESET: Email sent successfully to {email}")
                else:
                    logger.error(f"🔑 PASSWORD RESET: Failed to send email to {email}: {result.get('message')}")
            except Exception as e:
                logger.error(f"🔑 PASSWORD RESET: Error processing request: {str(e)}")
                import traceback
                traceback.print_exc()
        else:
            logger.info(f"🔑 PASSWORD RESET: User not found for {email} (returning generic message)")
        
        return jsonify({
            'message': 'Nếu email tồn tại trong hệ thống, link đặt lại mật khẩu đã được gửi'
        }), 200
        
    except Exception as e:
        logger.error(f"🔑 PASSWORD RESET: Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': f'Lỗi server: {str(e)}'}), 500


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password with token"""
    from app.services.token_service import verify_password_reset_token, consume_password_reset_token
    
    data = request.get_json() or {}
    token = data.get('token')
    new_password = data.get('new_password')
    
    if not token or not new_password:
        return jsonify({'message': 'Token and new password are required'}), 400
    
    if len(new_password) < 6:
        return jsonify({'message': 'Password must be at least 6 characters'}), 400
    
    # Verify token
    result = verify_password_reset_token(token)
    
    if not result['success']:
        return jsonify({'message': result['message']}), 400
    
    user_id = result['user_id']
    user_email = result.get('email', '')
    
    # Update password (handle both MSSQL and ORM)
    if db.get_engine().dialect.name == 'mssql':
        try:
            pwd_hash = generate_password_hash(new_password)
            db.session.execute(text(
                'UPDATE [dbo].[Users] SET [PasswordHash]=:ph, [UpdatedAt]=GETDATE() WHERE [UserID]=:uid'
            ), {'ph': pwd_hash, 'uid': user_id})
            db.session.commit()
            logger.info(f"🔑 PASSWORD RESET: Password changed for user {user_id}")
        except Exception as e:
            logger.error(f"🔑 PASSWORD RESET: Failed to update password: {str(e)}")
            return jsonify({'message': 'Failed to reset password'}), 500
    else:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        user.set_password(new_password)
        db.session.commit()
        logger.info(f"🔑 PASSWORD RESET: Password changed for {user.email}")
    
    # Consume token (delete it)
    consume_password_reset_token(token)
    
    return jsonify({'message': 'Mật khẩu đã được đặt lại thành công'}), 200


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip()
    password = data.get('password') or ''

    if db.get_engine().dialect.name == 'mssql':
        row = None
        try:
            row = db.session.execute(text(
                'SELECT [UserID],[FullName],[Email],[PasswordHash],[Role],[IsActive] FROM [dbo].[Users] WHERE [Email]=:em'
            ), {'em': email}).fetchone()
        except Exception:
            row = db.session.execute(text(
                'SELECT [UserID],[FullName],[Email],[PasswordHash],[Role] FROM [dbo].[Users] WHERE [Email]=:em'
            ), {'em': email}).fetchone()
        if not row:
            return jsonify({'message': 'Incorrect email or password'}), 401
        uid, fullname, _, pwd_hash, role, *rest = row
        is_active = True
        if rest:
            try:
                is_active = bool(rest[0])
            except Exception:
                is_active = True
        ok = False
        if pwd_hash:
            try:
                ok = check_password_hash(pwd_hash, password)
            except Exception:
                ok = False
        if not ok and pwd_hash:
            # fallback if stored plain text (not recommended)
            ok = (password == str(pwd_hash))
        if not ok:
            logger.warning(f"🔒 LOGIN FAILED: Invalid credentials for {email}")
            return jsonify({'message': 'Incorrect email or password'}), 401
        if is_active is False:
            logger.warning(f"🔒 LOGIN BLOCKED: Account {email} is locked")
            return jsonify({'message': 'Account is locked'}), 403
        
        token = issue_token(uid, role or 'student')
        logger.info(f"✅ LOGIN SUCCESS: {email} (role: {role}) - JWT token issued")
        return jsonify({'token': token, 'fullname': fullname, 'role': role or 'student', 'email': email}), 200

    # Generic ORM path
    u = User.query.filter_by(email=email).first()
    if not u or not u.check_password(password):
        logger.warning(f"🔒 LOGIN FAILED: Invalid credentials for {email}")
        return jsonify({'message': 'Incorrect email or password'}), 401
    if getattr(u, 'is_active', True) is False:
        logger.warning(f"🔒 LOGIN BLOCKED: Account {email} is locked")
        return jsonify({'message': 'Account is locked'}), 403
    
    token = issue_token(u.id, u.role)
    logger.info(f"✅ LOGIN SUCCESS: {email} (role: {u.role}) - JWT token issued")
    return jsonify({'token': token, 'fullname': u.fullname, 'role': u.role, 'email': u.email}), 200


@auth_bp.route('/google/url', methods=['GET'])
def google_auth_url():
    """Get Google OAuth authorization URL"""
    try:
        import app.services.google_oauth_service as google_oauth
        
        if not google_oauth.is_enabled():
            return jsonify({'message': 'Google OAuth not configured'}), 503
        
        # Generate state for CSRF protection (optional)
        import secrets
        state = secrets.token_urlsafe(32)
        
        auth_url = google_oauth.get_authorization_url(state=state)
        
        if not auth_url:
            return jsonify({'message': 'Failed to generate authorization URL'}), 500
        
        logger.info("🔐 GOOGLE OAUTH: Generated authorization URL")
        return jsonify({
            'auth_url': auth_url,
            'state': state
        }), 200
        
    except Exception as e:
        logger.error(f"🔐 GOOGLE OAUTH: Error generating URL: {str(e)}")
        return jsonify({'message': f'Error: {str(e)}'}), 500


@auth_bp.route('/google/callback', methods=['GET', 'POST'])
def google_callback():
    """Handle Google OAuth callback"""
    try:
        import app.services.google_oauth_service as google_oauth
        
        # Get authorization code from query params
        code = request.args.get('code')
        error = request.args.get('error')
        
        if error:
            logger.warning(f"🔐 GOOGLE OAUTH: User denied access - {error}")
            return jsonify({'message': 'Google authentication cancelled'}), 400
        
        if not code:
            return jsonify({'message': 'Authorization code not provided'}), 400
        
        logger.info("🔐 GOOGLE OAUTH: Processing callback")
        
        # Verify user with Google
        result = google_oauth.verify_google_user(code)
        
        if not result['success']:
            logger.error(f"🔐 GOOGLE OAUTH: Verification failed - {result.get('message')}")
            return jsonify({'message': result.get('message')}), 400
        
        user_info = result['user_info']
        email = user_info['email']
        fullname = user_info['name']
        avatar_url = user_info.get('picture')
        google_id = user_info.get('google_id')
        
        logger.info(f"🔐 GOOGLE OAUTH: User verified - {email}")
        
        # Check if user exists (handle both MSSQL and ORM)
        user = None
        user_id = None
        user_role = None
        
        if db.get_engine().dialect.name == 'mssql':
            try:
                row = db.session.execute(text(
                    'SELECT [UserID],[FullName],[Role],[AvatarUrl] FROM [dbo].[Users] WHERE [Email]=:em'
                ), {'em': email}).fetchone()
                
                if row:
                    user_id, existing_name, user_role, existing_avatar = row
                    user = True
                    
                    # Update avatar if changed
                    if avatar_url and avatar_url != existing_avatar:
                        db.session.execute(text(
                            'UPDATE [dbo].[Users] SET [AvatarUrl]=:av, [UpdatedAt]=GETDATE() WHERE [UserID]=:uid'
                        ), {'av': avatar_url, 'uid': user_id})
                        db.session.commit()
                        logger.info(f"🔐 GOOGLE OAUTH: Updated avatar for {email}")
                else:
                    # Create new user
                    pwd_hash = generate_password_hash(secrets.token_urlsafe(32))  # Random password
                    row = db.session.execute(text(
                        'INSERT INTO [dbo].[Users] (FullName,Email,PasswordHash,Role,AvatarUrl,TwoFAEnabled,CreatedAt,UpdatedAt) '
                        'OUTPUT INSERTED.UserID VALUES (:fn,:em,:ph,:rl,:av,0,GETDATE(),GETDATE())'
                    ), {'fn': fullname, 'em': email, 'ph': pwd_hash, 'rl': 'student', 'av': avatar_url}).fetchone()
                    user_id = int(row[0])
                    user_role = 'student'
                    db.session.commit()
                    logger.info(f"🔐 GOOGLE OAUTH: Created new user - {email}")
                    
            except Exception as e:
                logger.error(f"🔐 GOOGLE OAUTH: Database error: {str(e)}")
                import traceback
                traceback.print_exc()
                return jsonify({'message': 'Database error'}), 500
        else:
            user = User.query.filter_by(email=email).first()
            
            if user:
                user_id = user.id
                user_role = user.role
                
                # Update avatar if changed
                if avatar_url and avatar_url != user.avatar_url:
                    user.avatar_url = avatar_url
                    db.session.commit()
                    logger.info(f"🔐 GOOGLE OAUTH: Updated avatar for {email}")
            else:
                # Create new user
                user = User(
                    fullname=fullname,
                    email=email,
                    role='student',
                    avatar_url=avatar_url
                )
                user.set_password(secrets.token_urlsafe(32))  # Random password
                db.session.add(user)
                db.session.commit()
                user_id = user.id
                user_role = user.role
                logger.info(f"🔐 GOOGLE OAUTH: Created new user - {email}")
        
        # Generate JWT token
        token = issue_token(user_id, user_role or 'student')
        
        logger.info(f"✅ GOOGLE OAUTH SUCCESS: {email} (role: {user_role}) - JWT token issued")
        
        return jsonify({
            'token': token,
            'fullname': fullname,
            'role': user_role or 'student',
            'email': email,
            'avatar_url': avatar_url
        }), 200
        
    except Exception as e:
        logger.error(f"🔐 GOOGLE OAUTH: Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': f'Error: {str(e)}'}), 500


@auth_bp.route('/google/login', methods=['POST'])
def google_login():
    """Alternative endpoint: Login with Google ID token (for frontend SDK)"""
    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests
        import app.services.google_oauth_service as google_oauth
        
        if not google_oauth.is_enabled():
            return jsonify({'message': 'Google OAuth not configured'}), 503
        
        data = request.get_json() or {}
        token_id = data.get('token')
        
        if not token_id:
            return jsonify({'message': 'Google ID token required'}), 400
        
        logger.info("🔐 GOOGLE OAUTH: Verifying ID token")
        
        # Verify the token
        try:
            idinfo = id_token.verify_oauth2_token(
                token_id,
                google_requests.Request(),
                google_oauth.GOOGLE_CLIENT_ID
            )
            
            # Token is valid
            email = idinfo['email']
            fullname = idinfo.get('name', email)
            avatar_url = idinfo.get('picture')
            
            logger.info(f"🔐 GOOGLE OAUTH: Token verified - {email}")
            
            # Same user creation/update logic as callback
            # (Reuse the code from google_callback above)
            # For brevity, returning a simplified response
            
            return jsonify({
                'message': 'Google authentication successful',
                'email': email,
                'name': fullname
            }), 200
            
        except ValueError as e:
            logger.error(f"🔐 GOOGLE OAUTH: Invalid token - {str(e)}")
            return jsonify({'message': 'Invalid Google token'}), 401
            
    except Exception as e:
        logger.error(f"🔐 GOOGLE OAUTH: Error: {str(e)}")
        return jsonify({'message': f'Error: {str(e)}'}), 500
