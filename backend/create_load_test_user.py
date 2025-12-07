"""
Create test user for load testing
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models.user_model import User
from sqlalchemy import text

app = create_app()

with app.app_context():
    email = 'student@example.com'
    password = 'password123'
    
    print(f"Creating test user: {email}")
    
    # Check if user exists
    if db.get_engine().dialect.name == 'mssql':
        row = db.session.execute(text(
            'SELECT [UserID] FROM [dbo].[Users] WHERE [Email]=:em'
        ), {'em': email}).fetchone()
        
        if row:
            print(f"✅ User already exists: {email}")
        else:
            from werkzeug.security import generate_password_hash
            pwd_hash = generate_password_hash(password)
            
            db.session.execute(text(
                'INSERT INTO [dbo].[Users] (FullName,Email,PasswordHash,Role,TwoFAEnabled,CreatedAt,UpdatedAt) '
                'VALUES (:fn,:em,:ph,:rl,0,GETDATE(),GETDATE())'
            ), {'fn': 'Test Student', 'em': email, 'ph': pwd_hash, 'rl': 'student'})
            db.session.commit()
            print(f"✅ Created test user: {email} / {password}")
    else:
        user = User.query.filter_by(email=email).first()
        
        if user:
            print(f"✅ User already exists: {email}")
        else:
            user = User(fullname='Test Student', email=email, role='student')
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            print(f"✅ Created test user: {email} / {password}")
    
    print("\nYou can now run: python load_test.py")
