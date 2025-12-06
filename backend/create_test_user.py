"""
Create test user for load testing
"""
from app import create_app, db
from app.models.user_model import User
from sqlalchemy import text
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    print("Creating test user for load testing...")
    print("=" * 60)
    
    email = 'student@example.com'
    password = 'password123'
    fullname = 'Test Student'
    role = 'student'
    
    try:
        # Check if user exists
        if db.get_engine().dialect.name == 'mssql':
            exists = db.session.execute(text(
                'SELECT 1 FROM [dbo].[Users] WHERE [Email]=:e'
            ), {'e': email}).fetchone()
            
            if exists:
                print(f"❌ User {email} already exists!")
            else:
                # Create user
                pwd_hash = generate_password_hash(password)
                
                try:
                    row = db.session.execute(text(
                        'INSERT INTO [dbo].[Users] (FullName,Email,PasswordHash,Role,TwoFAEnabled,CreatedAt,UpdatedAt) '
                        'OUTPUT INSERTED.UserID VALUES (:fn,:em,:ph,:rl,0,GETDATE(),GETDATE())'
                    ), {'fn': fullname, 'em': email, 'ph': pwd_hash, 'rl': role}).fetchone()
                except Exception:
                    # Fallback for minimal columns
                    row = db.session.execute(text(
                        'INSERT INTO [dbo].[Users] (FullName,Email,PasswordHash,Role) '
                        'OUTPUT INSERTED.UserID VALUES (:fn,:em,:ph,:rl)'
                    ), {'fn': fullname, 'em': email, 'ph': pwd_hash, 'rl': role}).fetchone()
                
                db.session.commit()
                
                print(f"✅ Test user created successfully!")
                print(f"   Email: {email}")
                print(f"   Password: {password}")
                print(f"   Role: {role}")
                print(f"   User ID: {row[0]}")
        else:
            # ORM path
            existing = User.query.filter_by(email=email).first()
            if existing:
                print(f"❌ User {email} already exists!")
            else:
                user = User(fullname=fullname, email=email, role=role)
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                
                print(f"✅ Test user created successfully!")
                print(f"   Email: {email}")
                print(f"   Password: {password}")
                print(f"   Role: {role}")
        
        print("\n" + "=" * 60)
        print("You can now run load test:")
        print("  python load_test.py")
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        import traceback
        traceback.print_exc()
