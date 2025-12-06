# E-Learning Platform

Hệ thống quản lý học tập trực tuyến với đầy đủ chức năng cho Admin, Teacher và Student.

## 📋 Mục lục

- [Tính năng](#tính-năng)
- [Công nghệ sử dụng](#công-nghệ-sử-dụng)
- [Yêu cầu hệ thống](#yêu-cầu-hệ-thống)
- [Cài đặt](#cài-đặt)
- [Chạy dự án](#chạy-dự-án)
- [Tài khoản mặc định](#tài-khoản-mặc-định)
- [Cấu trúc dự án](#cấu-trúc-dự-án)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Tính năng

### Admin
- ✅ Quản lý người dùng (thêm, sửa, xóa, đổi role)
- ✅ Quản lý khóa học (xem, sửa, xóa)
- ✅ Quản lý enrollments (approve, reject)
- ✅ Xem audit logs
- ✅ Cấu hình hệ thống (SMTP, AI, upload limits)
- ✅ Monitoring & Performance tracking
- ✅ C&C Dashboard

### Teacher
- ✅ Tạo và quản lý khóa học
- ✅ Upload bài giảng (video, PDF, slides)
- ✅ Tạo và quản lý quiz
- ✅ Quản lý học viên (approve, reject, remove)
- ✅ Xem báo cáo học tập
- ✅ Gửi announcements

### Student
- ✅ Đăng ký và xem khóa học
- ✅ Học bài (video, PDF, materials)
- ✅ Làm quiz với auto-grading
- ✅ Theo dõi tiến độ học tập
- ✅ AI Chatbot hỗ trợ
- ✅ Placement Test (bài test đầu vào)

---

## 🛠 Công nghệ sử dụng

### Backend
- **Python 3.11+**
- **Flask** - Web framework
- **SQLAlchemy** - ORM
- **JWT** - Authentication
- **Redis** - Caching
- **MS SQL Server** - Database
- **Google Gemini AI** - Chatbot

### Frontend
- **React 18**
- **Material-UI** - UI components
- **React Router** - Routing
- **Axios** - HTTP client

---

## 💻 Yêu cầu hệ thống

### Phần mềm cần cài đặt:

1. **Python 3.11 trở lên**
   - Download: https://www.python.org/downloads/

2. **Node.js 18+ và npm**
   - Download: https://nodejs.org/

3. **MS SQL Server Express**
   - Download: https://www.microsoft.com/en-us/sql-server/sql-server-downloads
   - Hoặc dùng SQL Server đã có sẵn

4. **Redis** (Optional - cho caching)
   - Windows: https://github.com/microsoftarchive/redis/releases
   - Hoặc chạy không cần Redis (hệ thống tự fallback)

5. **Git**
   - Download: https://git-scm.com/downloads

---

## 📦 Cài đặt

### Bước 1: Clone dự án

```bash
git clone <repository-url>
cd perl-python-course
```

### Bước 2: Cài đặt Backend

```bash
# Di chuyển vào thư mục backend
cd backend

# Tạo virtual environment
python -m venv .venv

# Kích hoạt virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt
```

### Bước 3: Cấu hình Database

1. **Tạo database trong SQL Server:**
   - Mở SQL Server Management Studio (SSMS)
   - Tạo database mới tên `ELearningDB`

2. **Chạy script tạo tables:**
   ```bash
   # Trong SQL Server, chạy file:
   database/setup_database.sql
   ```

3. **Import câu hỏi Placement Test:**
   ```bash
   # Chạy file:
   database/placement_test_questions.sql
   ```

### Bước 4: Cấu hình Backend

Tạo file `.env` trong thư mục `backend/`:

```env
# Database Configuration
DB_TYPE=mssql
DB_SERVER=localhost\SQLEXPRESS
DB_NAME=ELearningDB
DB_TRUSTED_CONNECTION=yes

# JWT Secret
JWT_SECRET_KEY=your-secret-key-here-change-in-production

# Redis (Optional)
REDIS_URL=redis://localhost:6379/0

# Google Gemini AI (Optional - for chatbot)
GEMINI_API_KEY=your-gemini-api-key-here
```

**Lưu ý:** 
- Thay `localhost\SQLEXPRESS` bằng tên SQL Server instance của bạn
- Nếu không có Redis, hệ thống vẫn chạy bình thường
- Nếu không có Gemini API key, chatbot sẽ không hoạt động

### Bước 5: Cài đặt Frontend

```bash
# Mở terminal mới, di chuyển vào thư mục frontend
cd frontend

# Cài đặt dependencies
npm install
```

---

## 🚀 Chạy dự án

### Lựa chọn:

**Cách 1: Chạy trực tiếp** (Khuyến nghị cho development)
- Xem hướng dẫn chi tiết trong [SETUP_GUIDE.md](SETUP_GUIDE.md)

**Cách 2: Chạy với Docker** (Optional)
```bash
docker-compose up
```

---

### Chạy Backend (Cách 1)

```bash
# Trong thư mục backend (với venv đã activate)
cd backend
python app.py
```

Backend sẽ chạy tại: `http://localhost:5000`

### Chạy Frontend

```bash
# Mở terminal mới, trong thư mục frontend
cd frontend
npm start
```

Frontend sẽ chạy tại: `http://localhost:3000`

### Tạo tài khoản test

```bash
# Trong thư mục backend
cd backend
python create_test_user.py
```

Script sẽ tạo 3 tài khoản:
- Admin: `admin@test.com` / `admin123`
- Teacher: `teacher@test.com` / `teacher123`
- Student: `student@test.com` / `password123`

---

## 👤 Tài khoản mặc định

Sau khi chạy `create_test_user.py`:

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@test.com | admin123 |
| Teacher | teacher@test.com | teacher123 |
| Student | student@test.com | password123 |

---

## 📁 Cấu trúc dự án

```
perl-python-course/
├── backend/                    # Backend Flask
│   ├── app/                   # Application code
│   │   ├── controllers/       # Business logic
│   │   ├── models/           # Database models
│   │   ├── views/            # API endpoints
│   │   ├── services/         # Services (cache, jwt, etc)
│   │   └── middleware/       # Middleware (performance, etc)
│   ├── app.py                # Entry point
│   ├── config.py             # Configuration
│   └── requirements.txt      # Python dependencies
│
├── frontend/                  # Frontend React
│   ├── src/
│   │   ├── components/       # Reusable components
│   │   ├── pages/           # Page components
│   │   │   ├── admin/       # Admin pages
│   │   │   ├── teacher/     # Teacher pages
│   │   │   └── student/     # Student pages
│   │   ├── services/        # API services
│   │   └── utils/           # Utilities
│   └── package.json         # Node dependencies
│
├── database/                 # Database scripts
│   ├── setup_database.sql   # Create tables
│   └── placement_test_questions.sql
│
├── docs/                    # Documentation
└── README.md               # This file
```

---

## 🔧 Troubleshooting

### Lỗi: "Cannot connect to database"

**Giải pháp:**
1. Kiểm tra SQL Server đang chạy
2. Kiểm tra tên server trong `.env` file
3. Kiểm tra database `ELearningDB` đã được tạo chưa

```bash
# Test connection
python -c "import pyodbc; print(pyodbc.drivers())"
```

### Lỗi: "Redis connection failed"

**Giải pháp:**
- Redis không bắt buộc, hệ thống sẽ tự động fallback
- Nếu muốn dùng Redis, cài đặt và chạy Redis server
- Hoặc comment dòng `REDIS_URL` trong `.env`

### Lỗi: "Port 5000 already in use"

**Giải pháp:**
```bash
# Windows: Tìm process đang dùng port 5000
netstat -ano | findstr :5000

# Kill process (thay PID bằng số thực tế)
taskkill /PID <PID> /F
```

### Lỗi: "Module not found"

**Giải pháp:**
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Frontend không kết nối được Backend

**Giải pháp:**
1. Kiểm tra backend đang chạy tại `http://localhost:5000`
2. Kiểm tra CORS đã được enable trong backend
3. Kiểm tra API URL trong frontend code

---

## 📚 Tài liệu thêm

- [API Documentation](docs/API_DOCUMENTATION.md)
- [Architecture Overview](docs/ARCHITECTURE_OVERVIEW.md)
- [Demo Guide for Instructor](DEMO_GUIDE_FOR_INSTRUCTOR.md)
- [Hướng dẫn Demo (Tiếng Việt)](HUONG_DAN_DEMO_CHO_GIANG_VIEN.md)

---

## 🎓 Quality Scenarios đã implement

1. ✅ **Performance Monitoring** - Theo dõi hiệu suất hệ thống
2. ✅ **Security** - JWT authentication, RBAC
3. ✅ **Reliability** - Error handling, validation
4. ✅ **Scalability** - Redis caching, connection pooling
5. ✅ **Availability** - Health checks, graceful shutdown
6. ✅ **Admin Management** - Quản lý toàn hệ thống
7. ✅ **Teacher Upload** - Upload file với compression
8. ✅ **Placement Test** - Bài test đầu vào tự động
9. ✅ **AI Chatbot** - Hỗ trợ học viên bằng AI

---

## 👥 Team Members

- [Thêm tên thành viên nhóm ở đây]

---

## 📝 License

[Thêm license nếu cần]

---

## 🆘 Hỗ trợ

Nếu gặp vấn đề, vui lòng:
1. Check [Troubleshooting](#troubleshooting) section
2. Xem các file hướng dẫn trong thư mục `docs/`
3. Liên hệ team leader

---

**Chúc bạn code vui vẻ! 🚀**
