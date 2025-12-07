"""
Token Service
Generate and verify tokens for email verification and password reset
"""
import secrets
import hashlib
from datetime import datetime, timedelta
from app import db
from app.models.user_model import User
import logging

logger = logging.getLogger(__name__)


class TokenStore:
    """In-memory token store (can be replaced with Redis or database)"""
    _tokens = {}
    
    @classmethod
    def store(cls, token_hash, data, expires_in_seconds):
        """Store token with expiration"""
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in_seconds)
        cls._tokens[token_hash] = {
            'data': data,
            'expires_at': expires_at
        }
        logger.info(f"[Token] Stored token (expires in {expires_in_seconds}s)")
    
    @classmethod
    def get(cls, token_hash):
        """Get token data if not expired"""
        if token_hash not in cls._tokens:
            return None
        
        token_data = cls._tokens[token_hash]
        
        # Check expiration
        if datetime.utcnow() > token_data['expires_at']:
            del cls._tokens[token_hash]
            logger.info("[Token] Token expired and removed")
            return None
        
        return token_data['data']
    
    @classmethod
    def delete(cls, token_hash):
        """Delete token"""
        if token_hash in cls._tokens:
            del cls._tokens[token_hash]
            logger.info("[Token] Token deleted")
    
    @classmethod
    def cleanup_expired(cls):
        """Remove expired tokens"""
        now = datetime.utcnow()
        expired = [k for k, v in cls._tokens.items() if now > v['expires_at']]
        for k in expired:
            del cls._tokens[k]
        if expired:
            logger.info(f"[Token] Cleaned up {len(expired)} expired tokens")


def generate_token():
    """Generate a secure random token"""
    return secrets.token_urlsafe(32)


def hash_token(token):
    """Hash token for storage"""
    return hashlib.sha256(token.encode()).hexdigest()


def create_verification_token(user_id, email):
    """
    Create email verification token
    
    Returns:
        str: Token to send to user
    """
    token = generate_token()
    token_hash = hash_token(token)
    
    # Store token for 24 hours
    TokenStore.store(token_hash, {
        'type': 'email_verification',
        'user_id': user_id,
        'email': email
    }, expires_in_seconds=86400)  # 24 hours
    
    logger.info(f"[Token] Created verification token for user {user_id}")
    return token


def verify_email_token(token):
    """
    Verify email verification token
    
    Returns:
        dict: {'success': bool, 'user_id': int, 'message': str}
    """
    token_hash = hash_token(token)
    data = TokenStore.get(token_hash)
    
    if not data:
        return {
            'success': False,
            'message': 'Token không hợp lệ hoặc đã hết hạn'
        }
    
    if data['type'] != 'email_verification':
        return {
            'success': False,
            'message': 'Token không hợp lệ'
        }
    
    # Mark user as verified (if you have email_verified field)
    # For now, just delete token
    TokenStore.delete(token_hash)
    
    logger.info(f"[Token] Email verified for user {data['user_id']}")
    return {
        'success': True,
        'user_id': data['user_id'],
        'message': 'Email đã được xác nhận thành công'
    }


def create_password_reset_token(user_id, email):
    """
    Create password reset token
    
    Returns:
        str: Token to send to user
    """
    token = generate_token()
    token_hash = hash_token(token)
    
    # Store token for 1 hour
    TokenStore.store(token_hash, {
        'type': 'password_reset',
        'user_id': user_id,
        'email': email
    }, expires_in_seconds=3600)  # 1 hour
    
    logger.info(f"[Token] Created password reset token for user {user_id}")
    return token


def verify_password_reset_token(token):
    """
    Verify password reset token
    
    Returns:
        dict: {'success': bool, 'user_id': int, 'email': str, 'message': str}
    """
    token_hash = hash_token(token)
    data = TokenStore.get(token_hash)
    
    if not data:
        return {
            'success': False,
            'message': 'Token không hợp lệ hoặc đã hết hạn'
        }
    
    if data['type'] != 'password_reset':
        return {
            'success': False,
            'message': 'Token không hợp lệ'
        }
    
    # Don't delete token yet - will delete after password is reset
    logger.info(f"[Token] Password reset token verified for user {data['user_id']}")
    return {
        'success': True,
        'user_id': data['user_id'],
        'email': data.get('email', ''),
        'message': 'Token hợp lệ'
    }


def consume_password_reset_token(token):
    """
    Consume (delete) password reset token after use
    """
    token_hash = hash_token(token)
    TokenStore.delete(token_hash)
    logger.info("[Token] Password reset token consumed")
