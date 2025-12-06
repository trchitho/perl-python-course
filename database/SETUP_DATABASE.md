# Hướng Dẫn Setup Database

## 📋 Yêu Cầu

- SQL Server Express 2022 (hoặc cao hơn)
- ODBC Driver 18 for SQL Server
- SQL Server Management Studio (SSMS) - khuyến nghị

## 🚀 Cách 1: Setup Tự Động (Khuyến Nghị)

### Bước 1: Chạy Backend với Auto-Seed

Backend đã được cấu hình để tự động tạo database schema và seed data.

1. Mở file `backend/.env` và đảm bảo cấu hình đúng:

```env
# Database Configuration
MSSQL_SERVER=np:\\.\pipe\MSSQL$SQLEXPRESS\sql\query
MSSQL_DATABASE=ELearningDB
MSSQL_USERNAME=learning
MSSQL_PASSWORD=123
MSSQL_DRIVER=ODBC Driver 18 for SQL Server

# Auto Seed (tạo admin user tự động)
DEV_AUTO_SEED=1
```

2. Chạy backend:

```bash
cd backend
.venv\Scripts\activate
python app.py
```

Backend sẽ tự động:
- Tạo tất cả tables
- Tạo admin user: `admin@example.com` / `123456`

## 🔧 Cách 2: Setup Thủ Công với SQL Scripts

### Bước 1: Tạo Database và Tables

1. Mở SQL Server Management Studio (SSMS)
2. Connect đến SQL Server instance của bạn
3. Mở file `database/setup_database.sql`
4. Chạy script (F5)

Script sẽ tạo:
- Database `ELearningDB`
- Tất cả tables với relationships
- Default constraints
- Check constraints

### Bước 2: Tạo User với Password Hash Đúng

Vì password cần được hash bằng werkzeug (Python), bạn có 2 cách:

#### Cách 2a: Dùng Python Script

1. Tạo file `create_users.py` trong thư mục `backend`:

```python
from app import create_app, db
from app.models.user_model import User

app = create_app()

with app.app_context():
    # Tạo Admin
    admin = User(
        fullname='Admin User',
        email='admin@example.com',
        role='admin'
    )
    admin.set_password('123456')
    db.session.add(admin)
    
    # Tạo Teacher
    teacher = User(
        fullname='Nguyễn Văn A',
        email='teacher1@example.com',
        role='teacher'
    )
    teacher.set_password('123456')
    db.session.add(teacher)
    
    # Tạo Student
    student = User(
        fullname='Lê Văn C',
        email='student1@example.com',
        role='student'
    )
    student.set_password('123456')
    db.session.add(student)
    
    db.session.commit()
    print('✅ Users created successfully!')
```

2. Chạy script:

```bash
cd backend
.venv\Scripts\activate
python create_users.py
```

#### Cách 2b: Dùng Backend API

1. Chạy backend server
2. Dùng API để register users:

```bash
# Tạo Admin (cần modify backend để cho phép tạo admin qua API)
curl -X POST http://127.0.0.1:5000/api/auth/register ^
  -H "Content-Type: application/json" ^
  -d "{\"fullname\":\"Admin\",\"email\":\"admin@example.com\",\"password\":\"123456\",\"role\":\"admin\"}"
```

### Bước 3: Insert Sample Data (Tùy chọn)

Sau khi có users, bạn có thể chạy `database/seed_data.sql` để thêm:
- Sample courses
- Sample lessons
- Sample quizzes
- Sample enrollments

**Lưu ý**: Cần update UserID trong seed_data.sql cho phù hợp với ID thực tế.

## 🔍 Kiểm Tra Database

### Kiểm tra trong SSMS

```sql
-- Kiểm tra database đã tạo
USE ELearningDB;
GO

-- Xem danh sách tables
SELECT TABLE_NAME 
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_TYPE = 'BASE TABLE';

-- Kiểm tra users
SELECT UserID, FullName, Email, Role, CreatedAt 
FROM Users;

-- Kiểm tra courses
SELECT CourseID, Title, Category, Status 
FROM Courses;
```

### Kiểm tra qua Backend

```bash
# Test connection
curl http://127.0.0.1:5000/

# Test login
curl -X POST http://127.0.0.1:5000/api/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"admin@example.com\",\"password\":\"123456\"}"
```

## 📊 Database Schema

### Tables

1. **Users** - Người dùng (admin, teacher, student)
2. **Courses** - Khóa học
3. **Lessons** - Bài học trong khóa học
4. **Quizzes** - Bài kiểm tra
5. **QuizQuestions** - Câu hỏi trong quiz
6. **QuizResults** - Kết quả quiz của học viên
7. **Enrollments** - Đăng ký khóa học
8. **Progress** - Tiến độ học tập
9. **Announcements** - Thông báo
10. **AuditLogs** - Logs hành động admin
11. **ChatbotHistory** - Lịch sử chat với AI
12. **PlacementTests** - Bài test đầu vào

### Relationships

```
Users (1) ----< (N) Courses (Teacher)
Users (1) ----< (N) Enrollments (Student)
Courses (1) ----< (N) Lessons
Courses (1) ----< (N) Quizzes
Quizzes (1) ----< (N) QuizQuestions
Quizzes (1) ----< (N) QuizResults
Users (1) ----< (N) QuizResults
```

## ⚠️ Troubleshooting

### Lỗi: Cannot connect to SQL Server

**Giải pháp**:
1. Kiểm tra SQL Server đang chạy:
   ```bash
   # Mở Services (services.msc)
   # Tìm "SQL Server (SQLEXPRESS)" và start
   ```

2. Kiểm tra Named Pipes enabled:
   - Mở SQL Server Configuration Manager
   - SQL Server Network Configuration > Protocols for SQLEXPRESS
   - Enable "Named Pipes"
   - Restart SQL Server service

### Lỗi: Login failed for user 'learning'

**Giải pháp**:
1. Tạo SQL Server login:
   ```sql
   USE master;
   GO
   
   CREATE LOGIN learning WITH PASSWORD = '123';
   GO
   
   USE ELearningDB;
   GO
   
   CREATE USER learning FOR LOGIN learning;
   GO
   
   ALTER ROLE db_owner ADD MEMBER learning;
   GO
   ```

### Lỗi: ODBC Driver not found

**Giải pháp**:
1. Download và cài đặt ODBC Driver 18:
   https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

2. Kiểm tra driver đã cài:
   ```bash
   # Mở ODBC Data Sources (64-bit)
   # Tab "Drivers" - tìm "ODBC Driver 18 for SQL Server"
   ```

### Lỗi: Database already exists

**Giải pháp**:
```sql
-- Drop database nếu muốn tạo lại
USE master;
GO

DROP DATABASE ELearningDB;
GO

-- Sau đó chạy lại setup_database.sql
```

## 🔐 Security Notes

### Development
- Password mặc định: `123456` (chỉ dùng cho dev)
- SQL user: `learning` / `123` (chỉ dùng cho dev)

### Production
- Thay đổi tất cả passwords
- Sử dụng environment variables
- Enable SSL/TLS
- Restrict database user permissions
- Enable SQL Server authentication logs

## 📝 Default Accounts

Sau khi setup xong, bạn có thể login với:

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@example.com | 123456 |
| Teacher | teacher1@example.com | 123456 |
| Student | student1@example.com | 123456 |

## 🔄 Reset Database

Nếu muốn reset database về trạng thái ban đầu:

```sql
USE master;
GO

-- Drop database
DROP DATABASE ELearningDB;
GO

-- Chạy lại setup_database.sql
-- Chạy lại create_users.py hoặc seed_data.sql
```

## 📚 Tài Liệu Tham Khảo

- [SQL Server Documentation](https://learn.microsoft.com/en-us/sql/sql-server/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/)
