"""
Email Service
Send emails using SMTP (Gmail, Outlook, etc.)
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app
import logging

logger = logging.getLogger(__name__)

# Email configuration from environment
SMTP_ENABLED = os.getenv('SMTP_ENABLED', 'false').lower() == 'true'
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
SMTP_FROM_EMAIL = os.getenv('SMTP_FROM_EMAIL', SMTP_USERNAME)
SMTP_FROM_NAME = os.getenv('SMTP_FROM_NAME', 'E-Learning Platform')


def is_enabled():
    """Check if SMTP is configured"""
    return bool(SMTP_ENABLED and SMTP_USERNAME and SMTP_PASSWORD)


def send_email(to_email, subject, html_content, text_content=None):
    """
    Send email using SMTP
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML email body
        text_content: Plain text fallback (optional)
    
    Returns:
        dict: {'success': bool, 'message': str}
    """
    if not is_enabled():
        logger.warning("[Email] SMTP not configured, email not sent")
        return {
            'success': False,
            'message': 'Email service not configured'
        }
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
        msg['To'] = to_email
        
        # Add text and HTML parts
        if text_content:
            part1 = MIMEText(text_content, 'plain', 'utf-8')
            msg.attach(part1)
        
        part2 = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(part2)
        
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"[Email] Sent to {to_email}: {subject}")
        return {
            'success': True,
            'message': 'Email sent successfully'
        }
    
    except Exception as e:
        logger.error(f"[Email] Failed to send to {to_email}: {str(e)}")
        return {
            'success': False,
            'message': f'Failed to send email: {str(e)}'
        }


def send_verification_email(to_email, verification_token, user_name):
    """Send email verification link"""
    verification_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:5173')}/verify-email?token={verification_token}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .button {{ display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Xác Nhận Email</h1>
            </div>
            <div class="content">
                <p>Xin chào <strong>{user_name}</strong>,</p>
                <p>Cảm ơn bạn đã đăng ký tài khoản tại E-Learning Platform!</p>
                <p>Vui lòng click vào nút bên dưới để xác nhận email của bạn:</p>
                <div style="text-align: center;">
                    <a href="{verification_url}" class="button">Xác Nhận Email</a>
                </div>
                <p>Hoặc copy link sau vào trình duyệt:</p>
                <p style="word-break: break-all; color: #667eea;">{verification_url}</p>
                <p><strong>Lưu ý:</strong> Link này sẽ hết hạn sau 24 giờ.</p>
            </div>
            <div class="footer">
                <p>© 2024 E-Learning Platform. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Xin chào {user_name},
    
    Cảm ơn bạn đã đăng ký tài khoản tại E-Learning Platform!
    
    Vui lòng click vào link sau để xác nhận email:
    {verification_url}
    
    Link này sẽ hết hạn sau 24 giờ.
    
    © 2024 E-Learning Platform
    """
    
    return send_email(to_email, "Xác nhận email - E-Learning Platform", html_content, text_content)


def send_password_reset_email(to_email, reset_token, user_name):
    """Send password reset link"""
    reset_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:5173')}/reset-password?token={reset_token}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .button {{ display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 10px; margin: 15px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Đặt Lại Mật Khẩu</h1>
            </div>
            <div class="content">
                <p>Xin chào <strong>{user_name}</strong>,</p>
                <p>Chúng tôi nhận được yêu cầu đặt lại mật khẩu cho tài khoản của bạn.</p>
                <p>Click vào nút bên dưới để đặt lại mật khẩu:</p>
                <div style="text-align: center;">
                    <a href="{reset_url}" class="button">Đặt Lại Mật Khẩu</a>
                </div>
                <p>Hoặc copy link sau vào trình duyệt:</p>
                <p style="word-break: break-all; color: #667eea;">{reset_url}</p>
                <div class="warning">
                    <strong>⚠️ Lưu ý:</strong>
                    <ul>
                        <li>Link này sẽ hết hạn sau 1 giờ</li>
                        <li>Nếu bạn không yêu cầu đặt lại mật khẩu, vui lòng bỏ qua email này</li>
                        <li>Không chia sẻ link này với bất kỳ ai</li>
                    </ul>
                </div>
            </div>
            <div class="footer">
                <p>© 2024 E-Learning Platform. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Xin chào {user_name},
    
    Chúng tôi nhận được yêu cầu đặt lại mật khẩu cho tài khoản của bạn.
    
    Click vào link sau để đặt lại mật khẩu:
    {reset_url}
    
    ⚠️ Lưu ý:
    - Link này sẽ hết hạn sau 1 giờ
    - Nếu bạn không yêu cầu đặt lại mật khẩu, vui lòng bỏ qua email này
    
    © 2024 E-Learning Platform
    """
    
    return send_email(to_email, "Đặt lại mật khẩu - E-Learning Platform", html_content, text_content)


def send_welcome_email(to_email, user_name):
    """Send welcome email after successful registration"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .button {{ display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 Chào Mừng Đến Với E-Learning!</h1>
            </div>
            <div class="content">
                <p>Xin chào <strong>{user_name}</strong>,</p>
                <p>Chúc mừng bạn đã đăng ký thành công tài khoản tại E-Learning Platform!</p>
                <p>Bạn có thể bắt đầu khám phá các khóa học và học tập ngay bây giờ.</p>
                <div style="text-align: center;">
                    <a href="{os.getenv('FRONTEND_URL', 'http://localhost:5173')}/login" class="button">Đăng Nhập Ngay</a>
                </div>
                <p>Chúc bạn học tập vui vẻ! 📚</p>
            </div>
            <div class="footer">
                <p>© 2024 E-Learning Platform. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(to_email, "Chào mừng đến với E-Learning Platform! 🎉", html_content)
