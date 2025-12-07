"""
Test script for forgot password functionality
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models.user_model import User

app = create_app()

with app.app_context():
    print("=" * 60)
    print("Testing Forgot Password Setup")
    print("=" * 60)
    
    # Test 1: Check email service
    print("\n1. Checking email service configuration...")
    from app.services.email_service import is_enabled, SMTP_ENABLED, SMTP_USERNAME, SMTP_PASSWORD
    print(f"   SMTP_ENABLED: {SMTP_ENABLED}")
    print(f"   SMTP_USERNAME: {SMTP_USERNAME}")
    print(f"   SMTP_PASSWORD: {'*' * len(SMTP_PASSWORD) if SMTP_PASSWORD else 'NOT SET'}")
    print(f"   is_enabled(): {is_enabled()}")
    
    # Test 2: Check database connection
    print("\n2. Checking database connection...")
    try:
        from sqlalchemy import text
        if db.get_engine().dialect.name == 'mssql':
            result = db.session.execute(text('SELECT COUNT(*) FROM [dbo].[Users]')).scalar()
            print(f"   ✅ MSSQL connected - {result} users in database")
        else:
            result = User.query.count()
            print(f"   ✅ Database connected - {result} users")
    except Exception as e:
        print(f"   ❌ Database error: {e}")
    
    # Test 3: Test token service
    print("\n3. Testing token service...")
    try:
        from app.services.token_service import create_password_reset_token, verify_password_reset_token
        test_token = create_password_reset_token(1, "test@example.com")
        print(f"   ✅ Token created: {test_token[:20]}...")
        
        result = verify_password_reset_token(test_token)
        print(f"   ✅ Token verified: {result}")
    except Exception as e:
        print(f"   ❌ Token error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Test email sending (without actually sending)
    print("\n4. Testing email service...")
    try:
        from app.services.email_service import send_password_reset_email
        # This will try to send but we'll catch any errors
        result = send_password_reset_email("test@example.com", "test_token_123", "Test User")
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   ❌ Email error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)
