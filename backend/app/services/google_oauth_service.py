"""
Google OAuth 2.0 Service
Handle Google Sign-In authentication
"""
import os
import requests
import logging
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

# Google OAuth configuration
GOOGLE_OAUTH_ENABLED = os.getenv('GOOGLE_OAUTH_ENABLED', 'false').lower() == 'true'
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')
GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:5000/api/auth/google/callback')

# Google OAuth URLs
GOOGLE_AUTH_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
GOOGLE_TOKEN_URL = 'https://oauth2.googleapis.com/token'
GOOGLE_USERINFO_URL = 'https://www.googleapis.com/oauth2/v2/userinfo'


def is_enabled():
    """Check if Google OAuth is configured"""
    return bool(GOOGLE_OAUTH_ENABLED and GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)


def get_authorization_url(state=None):
    """
    Generate Google OAuth authorization URL
    
    Args:
        state: Optional state parameter for CSRF protection
    
    Returns:
        str: Authorization URL to redirect user to
    """
    if not is_enabled():
        return None
    
    params = {
        'client_id': GOOGLE_CLIENT_ID,
        'redirect_uri': GOOGLE_REDIRECT_URI,
        'response_type': 'code',
        'scope': 'openid email profile',
        'access_type': 'offline',
        'prompt': 'consent',
    }
    
    if state:
        params['state'] = state
    
    auth_url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    logger.info("[Google OAuth] Generated authorization URL")
    return auth_url


def exchange_code_for_token(code):
    """
    Exchange authorization code for access token
    
    Args:
        code: Authorization code from Google
    
    Returns:
        dict: {'success': bool, 'access_token': str, 'message': str}
    """
    if not is_enabled():
        return {
            'success': False,
            'message': 'Google OAuth not configured'
        }
    
    try:
        data = {
            'code': code,
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'redirect_uri': GOOGLE_REDIRECT_URI,
            'grant_type': 'authorization_code',
        }
        
        response = requests.post(GOOGLE_TOKEN_URL, data=data, timeout=10)
        
        if response.status_code != 200:
            logger.error(f"[Google OAuth] Token exchange failed: {response.text}")
            return {
                'success': False,
                'message': 'Failed to exchange code for token'
            }
        
        token_data = response.json()
        logger.info("[Google OAuth] Successfully exchanged code for token")
        
        return {
            'success': True,
            'access_token': token_data.get('access_token'),
            'id_token': token_data.get('id_token'),
            'refresh_token': token_data.get('refresh_token'),
        }
    
    except Exception as e:
        logger.error(f"[Google OAuth] Error exchanging code: {str(e)}")
        return {
            'success': False,
            'message': f'Error: {str(e)}'
        }


def get_user_info(access_token):
    """
    Get user information from Google
    
    Args:
        access_token: Google access token
    
    Returns:
        dict: {'success': bool, 'user_info': dict, 'message': str}
    """
    try:
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        response = requests.get(GOOGLE_USERINFO_URL, headers=headers, timeout=10)
        
        if response.status_code != 200:
            logger.error(f"[Google OAuth] Failed to get user info: {response.text}")
            return {
                'success': False,
                'message': 'Failed to get user information'
            }
        
        user_info = response.json()
        logger.info(f"[Google OAuth] Retrieved user info for {user_info.get('email')}")
        
        return {
            'success': True,
            'user_info': {
                'email': user_info.get('email'),
                'name': user_info.get('name'),
                'picture': user_info.get('picture'),
                'verified_email': user_info.get('verified_email', False),
                'google_id': user_info.get('id'),
            }
        }
    
    except Exception as e:
        logger.error(f"[Google OAuth] Error getting user info: {str(e)}")
        return {
            'success': False,
            'message': f'Error: {str(e)}'
        }


def verify_google_user(code):
    """
    Complete OAuth flow: exchange code and get user info
    
    Args:
        code: Authorization code from Google
    
    Returns:
        dict: {'success': bool, 'user_info': dict, 'message': str}
    """
    # Exchange code for token
    token_result = exchange_code_for_token(code)
    
    if not token_result['success']:
        return token_result
    
    # Get user information
    user_result = get_user_info(token_result['access_token'])
    
    if not user_result['success']:
        return user_result
    
    return {
        'success': True,
        'user_info': user_result['user_info'],
        'message': 'Successfully authenticated with Google'
    }
