# HƯỚNG DẪN CÀI ĐẶT CHI TIẾT

Hướng dẫn từng bước để cài đặt và chạy dự án E-Learning Platform.

---

## 🎯 CHỌN CÁCH CHẠY DỰ ÁN

Bạn có thể chọn 1 trong 2 cách:

### ✅ **Cách 1: Chạy trực tiếp (KHUYẾN NGHỊ)**
- ✅ Đơn giản, dễ debug
- ✅ Không cần Docker
- ✅ Phù hợp cho development
- ⏱️ Setup: ~30 phút

👉 **Làm theo hướng dẫn bên dưới**

### 🐳 **Cách 2: Chạy bằng Docker**
- ✅ Tất cả services trong containers
- ✅ Không cần cài Python, Node.js
- ⚠️ Vẫn cần SQL Server riêng
- ⏱️ Setup: ~15 phút (nếu đã có Docker)

👉 **Xem phần [Chạy với Docker](#chạy-với-docker) ở cuối file**

---

## 📋 CHUẨN BỊ (Cách 1 - Chạy trực tiếp)

### 1. Cài đặt Python 3.11+

**Windows:**
1. Download Python từ: https://www.python.org/downloads/
2. Chạy installer
3. ✅ **QUAN TRỌNG:** Tick vào "Add Python to PATH"
4. Click "Install Now"
5. Kiểm tra:
   ```bash
   python --version
   ```

### 2. Cài đặt Node.js 18+

**Windows:**
1. Download từ: https://nodejs.org/
2. Chọn "LTS" version
3. Chạy installer với default settings
4. Kiểm tra:
   ```bash
   node --version
   npm --version
   ```

### 3. Cài đặt SQL Server

**Nếu chưa có SQL Server:**
1. Download SQL Server Express: https://www.microsoft.com/en-us/sql-server/sql-server-downloads
2. Download SQL Server Management Studio (SSMS): https://aka.ms/ssmsfullsetup
3. Cài đặt cả hai
4. Mở SSMS, connect với:
   - Server name: `localhost\SQLEXPRESS`
   - Authentication: Windows Authentication

### 4. Cài đặt Git (nếu chưa có)

Download từ: https://git-scm.com/downloads

---

## 🚀 CÀI ĐẶT DỰ ÁN

### BƯỚC 1: Clone dự án

```bash
# Clone repository
git clone <repository-url>

# Di chuyển vào thư mục dự án
cd perl-python-course
```

---

### BƯỚC 2: Setup Database

#### 2.1. Tạo Database

1. Mở **SQL Server Management Studio (SSMS)**
2. Connect vào SQL Server
3. Click phải vào "Databases" → "New Database"
4. Đặt tên: `ELearningDB`
5. Click OK

#### 2.2. Chạy Script tạo Tables

1. Trong SSMS, click "New Query"
2. Mở file `database/setup_database.sql`
3. Copy toàn bộ nội dung vào Query window
4. Chọn database `ELearningDB` trong dropdown
5. Click "Execute" (hoặc F5)
6. Kiểm tra: Refresh "Tables" folder, phải thấy các tables mới

#### 2.3. Import Placement Test Questions

1. Mở file `database/placement_test_questions.sql`
2. Copy nội dung vào Query window
3. Execute
4. Kiểm tra: Query `SELECT COUNT(*) FROM PlacementQuestions` → Phải có 30 rows

---

### BƯỚC 3: Setup Backend

#### 3.1. Tạo Virtual Environment

```bash
# Di chuyển vào thư mục backend
cd backend

# Tạo virtual environment
python -m venv .venv

# Kích hoạt virtual environment
# Windows CMD:
.venv\Scripts\activate.bat

# Windows PowerShell:
.venv\Scripts\Activate.ps1

# Linux/Mac:
source .venv/bin/activate
```

**Lưu ý:** Sau khi activate, bạn sẽ thấy `(.venv)` ở đầu dòng lệnh.

#### 3.2. Cài đặt Dependencies

```bash
# Đảm bảo đang ở trong backend folder và venv đã activate
pip install -r requirements.txt
```

**Nếu gặp lỗi với pyodbc:**
- Download ODBC Driver 17 for SQL Server: https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
- Cài đặt và chạy lại `pip install pyodbc`

#### 3.3. Tạo file .env

Tạo file `.env` trong thư mục `backend/`:

```env
# Database Configuration
DB_TYPE=mssql
DB_SERVER=localhost\SQLEXPRESS
DB_NAME=ELearningDB
DB_TRUSTED_CONNECTION=yes

# JWT Secret (đổi thành chuỗi random trong production)
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production

# Redis (Optional - comment out nếu không dùng)
REDIS_URL=redis://localhost:6379/0

# Google Gemini AI (Optional - để trống nếu không có)
GEMINI_API_KEY=
```

**Chỉnh sửa:**
- Thay `localhost\SQLEXPRESS` bằng tên SQL Server instance của bạn
- Nếu dùng SQL Authentication, thêm:
  ```env
  DB_USER=your_username
  DB_PASSWORD=your_password
  DB_TRUSTED_CONNECTION=no
  ```

#### 3.4. Tạo tài khoản test

```bash
# Trong thư mục backend với venv activated
python create_test_user.py
```

Sẽ tạo 3 tài khoản:
- Admin: `admin@test.com` / `admin123`
- Teacher: `teacher@test.com` / `teacher123`
- Student: `student@test.com` / `password123`

---

### BƯỚC 4: Setup Frontend

```bash
# Mở terminal MỚI (không cần venv)
# Di chuyển vào thư mục frontend
cd frontend

# Cài đặt dependencies
npm install
```

**Nếu gặp lỗi:**
```bash
# Xóa node_modules và package-lock.json
rm -rf node_modules package-lock.json

# Cài lại
npm install
```

---

## ▶️ CHẠY DỰ ÁN

### Terminal 1: Chạy Backend

```bash
# Di chuyển vào backend
cd backend

# Activate venv (nếu chưa)
.venv\Scripts\activate

# Chạy server
python app.py
```

**Kết quả mong đợi:**
```
[Config] Using MSSQL via pyodbc...
[Cache] Redis enabled - TTL: 300s
[Performance] Monitoring enabled
 * Running on http://127.0.0.1:5000
```

**Nếu thấy lỗi Redis:** Không sao, hệ thống vẫn chạy bình thường.

### Terminal 2: Chạy Frontend

```bash
# Mở terminal MỚI
# Di chuyển vào frontend
cd frontend

# Chạy dev server
npm start
```

**Kết quả mong đợi:**
```
Compiled successfully!

Local:            http://localhost:3000
```

Browser sẽ tự động mở `http://localhost:3000`

---

## ✅ KIỂM TRA

### 1. Test Backend

Mở browser: `http://localhost:5000/health`

Kết quả:
```json
{
  "status": "healthy",
  "checks": {
    "database": {"status": "healthy"},
    "cache": {"status": "degraded"}
  }
}
```

### 2. Test Frontend

1. Mở `http://localhost:3000`
2. Click "Login"
3. Đăng nhập với:
   - Email: `student@test.com`
   - Password: `password123`
4. Nếu vào được Dashboard → Thành công! ✅

---

## 🔧 TROUBLESHOOTING

### Lỗi: "Cannot connect to database"

**Nguyên nhân:** SQL Server không chạy hoặc connection string sai

**Giải pháp:**
1. Mở SQL Server Configuration Manager
2. Kiểm tra SQL Server service đang chạy
3. Kiểm tra tên server trong `.env`:
   ```bash
   # Test connection
   python -c "import pyodbc; print(pyodbc.drivers())"
   ```

### Lỗi: "pyodbc.Error: Data source name not found"

**Giải pháp:**
1. Cài ODBC Driver 17: https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
2. Restart terminal
3. Chạy lại `pip install pyodbc`

### Lỗi: "Port 5000 already in use"

**Giải pháp:**
```bash
# Tìm process
netstat -ano | findstr :5000

# Kill process (thay 1234 bằng PID thực tế)
taskkill /PID 1234 /F
```

### Lỗi: "npm ERR! code ELIFECYCLE"

**Giải pháp:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

### Backend chạy nhưng Frontend không kết nối được

**Giải pháp:**
1. Kiểm tra backend đang chạy: `http://localhost:5000/health`
2. Kiểm tra CORS trong backend
3. Clear browser cache (Ctrl + Shift + Delete)

---

## 📝 LƯU Ý QUAN TRỌNG

### Khi làm việc nhóm:

1. **Luôn pull code mới nhất:**
   ```bash
   git pull origin main
   ```

2. **Sau khi pull, cài lại dependencies:**
   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt
   
   # Frontend
   cd frontend
   npm install
   ```

3. **Không commit file .env:**
   - File `.env` chứa thông tin nhạy cảm
   - Mỗi người tự tạo `.env` của mình

4. **Không commit node_modules và .venv:**
   - Đã có trong `.gitignore`
   - Mỗi người tự cài dependencies

### Trước khi demo:

1. ✅ Backend đang chạy
2. ✅ Frontend đang chạy
3. ✅ Database có dữ liệu test
4. ✅ Đã test login với 3 roles

---

## 🎯 NEXT STEPS

Sau khi setup xong:

1. Đọc [DEMO_GUIDE_FOR_INSTRUCTOR.md](DEMO_GUIDE_FOR_INSTRUCTOR.md)
2. Đọc [HUONG_DAN_DEMO_CHO_GIANG_VIEN.md](HUONG_DAN_DEMO_CHO_GIANG_VIEN.md)
3. Test tất cả chức năng
4. Chuẩn bị demo

---

**Chúc bạn setup thành công! 🎉**

Nếu gặp vấn đề, hãy check lại từng bước hoặc liên hệ team leader.

---

## 🐳 CHẠY VỚI DOCKER (Tùy chọn)

### Yêu cầu:
- Docker Desktop đã cài đặt
- SQL Server vẫn cần chạy riêng (không có trong Docker)

### Bước 1: Cài Docker Desktop

Download từ: https://www.docker.com/products/docker-desktop/

### Bước 2: Setup Database

**Vẫn cần làm như Cách 1:**
1. Cài SQL Server
2. Tạo database `ELearningDB`
3. Chạy `setup_database.sql`
4. Import `placement_test_questions.sql`

### Bước 3: Tạo file .env

Tạo `backend/.env` như hướng dẫn ở trên.

**Lưu ý:** Thay `localhost` bằng `host.docker.internal`:
```env
DB_SERVER=host.docker.internal\SQLEXPRESS
```

### Bước 4: Chạy Docker Compose

```bash
# Trong thư mục gốc dự án
docker-compose up
```

**Kết quả:**
- Backend: `http://localhost:5000`
- Frontend: `http://localhost:3000`
- Redis: `localhost:6379` (tự động)

### Bước 5: Tạo tài khoản test

```bash
# Chạy trong container
docker-compose exec backend python create_test_user.py
```

### Dừng Docker

```bash
# Dừng services
docker-compose down

# Dừng và xóa volumes
docker-compose down -v
```

---

## 🤔 NÊN CHỌN CÁCH NÀO?

### Chọn **Cách 1 (Trực tiếp)** nếu:
- ✅ Bạn muốn debug code dễ dàng
- ✅ Bạn đang develop/sửa code
- ✅ Bạn chưa quen Docker
- ✅ Máy không đủ mạnh chạy Docker

### Chọn **Cách 2 (Docker)** nếu:
- ✅ Bạn đã quen Docker
- ✅ Bạn muốn môi trường isolated
- ✅ Bạn cần deploy lên server
- ✅ Bạn không muốn cài Python/Node.js

**Khuyến nghị:** Dùng **Cách 1** cho development, **Cách 2** cho production.

---

**Chúc bạn thành công! 🚀**
