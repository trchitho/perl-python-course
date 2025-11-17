Tổng quan dự án — E‑Learning cho người mới bắt đầu CNTT

Kiến trúc
- Backend: Flask REST API theo mô hình MVC tại `backend/app/`
- Frontend: HTML/CSS/JS tĩnh tại `frontend/`
- CSDL: Mặc định SQLite (tự tạo file `backend/app.db`). Có thể dùng SQL Server qua ODBC nếu cấu hình môi trường.

Khởi chạy nhanh (Windows/PowerShell)
1) Cài phụ thuộc
   - `py -m venv .venv`
   - `.\.venv\Scripts\Activate.ps1`
   - `pip install -r requirements.txt`
2) Chạy backend
   - `py backend\app.py`
   - Kiểm tra: http://127.0.0.1:5000/ (API ở `/api/*`)
3) Frontend
   - Mở `frontend\index.html` hoặc dùng server tĩnh.

Cấu hình môi trường (tùy chọn)
- `DATABASE_URL` (ưu tiên cao nhất)
- `DB_DIALECT=mssql` để dùng SQL Server
- `MSSQL_SERVER`, `MSSQL_DATABASE`, `MSSQL_USERNAME`, `MSSQL_PASSWORD`, `MSSQL_DRIVER`

Các route chính
- `/api/auth/*`: đăng ký, đăng nhập (JWT)
- `/api/student/*`: khóa học/ bài học, bài kiểm tra cho học viên
- `/api/teacher/*`: thống kê, quản lý khóa/ bài/ đề cho giáo viên
- `/api/admin/*`: quản trị người dùng, ghi log, cài đặt, thống kê
- `/api/ai/chat`: chatbot mẫu (stub)

Những sửa lỗi/ cải tiến đã làm
- Mặc định dùng SQLite để chạy local dễ dàng; MSSQL là tùy chọn thông qua biến môi trường.
- Chuẩn hóa model `users` (snake_case) cho nhánh CSDL tổng quát, fix lỗi join/ khóa ngoại.
- Bổ sung xử lý riêng cho MSSQL ở luồng quản trị người dùng (raw SQL), đảm bảo tương thích khi tên bảng/ cột khác.

