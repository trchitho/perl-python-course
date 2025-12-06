# 🎬 Hướng Dẫn Demo 9 Kịch Bản Quality Attributes

> Tài liệu này hướng dẫn chi tiết cách demo 9 kịch bản Quality Attributes cho giảng viên đánh giá dự án.

**Thời gian demo:** 20-25 phút  
**Người thực hiện:** Thành viên nhóm  
**Đối tượng:** Giảng viên đánh giá  

---

## 📋 Mục Lục

- [Chuẩn Bị Trước Demo](#-chuẩn-bị-trước-demo)
- [PHẦN 1: USABILITY (5 phút)](#-phần-1-usability-5-phút)
- [PHẦN 2: PERFORMANCE (7 phút)](#-phần-2-performance-7-phút)
- [PHẦN 3: SECURITY (8 phút)](#-phần-3-security-8-phút)
- [Câu Hỏi Thường Gặp](#-câu-hỏi-thường-gặp)
- [Checklist Demo](#-checklist-demo)

---

## 🎯 Chuẩn Bị Trước Demo

### 1. Khởi Động Hệ Thống

**Terminal 1 - Backend:**
```bash
cd backend
.venv\Scripts\activate  # Windows
python app.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Kiểm tra:**
- ✅ Backend chạy tại: `http://localhost:5000`
- ✅ Frontend chạy tại: `http://localhost:5173`
- ✅ Không có lỗi trong console

### 2. Chuẩn Bị Dữ Liệu Test

```bash
cd backend
python create_teacher_test_data.py
```

**Kết quả:**
- ✅ 1 teacher account
- ✅ 3 courses
- ✅ 9 lessons
- ✅ 3 quizzes
- ✅ 5 students
- ✅ 15 enrollments

### 3. Mở Các Tools Cần Thiết

- ✅ Browser (Chrome/Edge) với DevTools (F12)
- ✅ SQL Server Management Studio (để show database)
- ✅ Backend terminal (để show logs)
- ✅ Timer/stopwatch (để đo response time)

### 4. Test Accounts

| Role | Email | Password |
|------|-------|----------|
| Student | student1@test.com | password123 |
| Teacher | teacher1@test.com | password123 |
| Admin | admin@test.com | admin123 |

---

## 🎨 PHẦN 1: USABILITY (5 phút)

### Scenario 1: Lesson Navigation (2 phút)

**Mục tiêu:** Chứng minh người học mới có thể điều hướng dễ dàng

**Demo Steps:**

1. **Login as Student**
   ```
   Email: student1@test.com
   Password: password123
   ```

2. **Navigate to Courses**
   - Click "Courses" trong sidebar
   - Quan sát: Menu rõ ràng, icons dễ hiểu

3. **View Course Details**
   - Click vào course "Python Programming"
   - Quan sát: Hiển thị danh sách lessons

4. **Navigate Between Lessons**
   - Click vào lesson đầu tiên
   - Quan sát: 
     - ✅ Breadcrumbs hiển thị vị trí
     - ✅ Previous/Next buttons rõ ràng
     - ✅ Progress indicator
     - ✅ Chuyển đổi mượt mà < 3s

**Success Criteria:**
- ✅ Navigation actions ≤ 3 seconds
- ✅ No UI errors
- ✅ Clear navigation buttons

**Điểm Nhấn:**
- "Như các thầy cô thấy, giao diện rất trực quan với Material-UI"
- "Navigation buttons rõ ràng, người dùng mới dễ hiểu"
- "Có breadcrumbs để biết đang ở đâu"

---

### Scenario 2: Quiz Interaction (2 phút)

**Mục tiêu:** Chứng minh quiz interaction mượt mà và trực quan

**Demo Steps:**

1. **Access Quiz**
   - Từ lesson page, click "Take Quiz"
   - Hoặc navigate to "Quizzes" section

2. **Answer Questions**
   - Select answer (A, B, C, or D)
   - Quan sát: Response time < 0.5s
   - Show: Answer được highlight ngay lập tức

3. **Navigate Questions**
   - Click "Next Question"
   - Click "Previous Question"
   - Quan sát: Transition < 1s, mượt mà

4. **Submit Quiz**
   - Review answers
   - Click "Submit"
   - View results immediately

**Success Criteria:**
- ✅ Answer selection latency ≤ 0.5s
- ✅ Question navigation ≤ 1s
- ✅ 0 confusing UI elements
- ✅ Clear progress indicator

**Điểm Nhấn:**
- "Quiz UI rất responsive, click là có phản hồi ngay"
- "Progress bar giúp biết đã làm được bao nhiêu câu"
- "Có thể quay lại xem câu trước, rất tiện"

---

### Scenario 3: AI Chatbot Help (1 phút)

**Mục tiêu:** Chứng minh chatbot dễ sử dụng và hữu ích

**Demo Steps:**

1. **Open Chatbot**
   - Click "Chatbot" trong sidebar
   - Quan sát: Chatbox opens smoothly

2. **Ask Question**
   - Type: "What is RAM?"
   - Click Send
   - Quan sát: Message sent < 1s

3. **Receive Answer**
   - Wait for AI response
   - Quan sát: 
     - ✅ Loading indicator hiển thị
     - ✅ Response < 6s
     - ✅ Answer formatted đẹp (markdown)

**Success Criteria:**
- ✅ Message input/send ≤ 1s
- ✅ 0 UI confusion points
- ✅ Clear instructions
- ✅ Readable answer format

**Điểm Nhấn:**
- "Chatbot interface rất clean và dễ dùng"
- "Có loading indicator khi AI đang suy nghĩ"
- "Câu trả lời được format đẹp, dễ đọc"

---

## ⚡ PHẦN 2: PERFORMANCE (7 phút)

### Scenario 4: Lesson Access Speed (2 phút)

**Mục tiêu:** Chứng minh bài học load nhanh < 5s

**Demo Steps:**

1. **Open DevTools**
   - Press F12
   - Go to Network tab
   - Clear network log

2. **Open Lesson**
   - Navigate to any lesson
   - Start timer when clicking

3. **Measure Load Time**
   - Quan sát: Page loads completely
   - Check Network tab: "Load" time at bottom
   - Verify: < 5s

4. **Show Response Time Header**
   - Click on API request
   - Show `X-Response-Time` header
   - Example: `X-Response-Time: 0.234s`

**Success Criteria:**
- ✅ Page load ≤ 5s
- ✅ Video buffer ≤ 4s
- ✅ 0 broken elements

**Điểm Nhấn:**
- "Như các thầy cô thấy trong Network tab, page load rất nhanh"
- "Mỗi request đều có X-Response-Time header để track performance"
- "Video buffer nhanh, không bị lag"

---

### Scenario 5: Course Search Performance (2 phút)

**Mục tiêu:** Chứng minh search results < 1s

**Demo Steps:**

1. **Go to Course Catalog**
   - Navigate to "Courses" page
   - Open DevTools Network tab

2. **Use Search**
   - Type keyword: "Python"
   - Quan sát: Results appear quickly

3. **Measure Response Time**
   - Check Network tab
   - Find API request: `GET /api/student/all-courses`
   - Check response time
   - Verify: < 1s

4. **Show Backend Logs**
   - Switch to backend terminal
   - Show log: `✅ GET /api/student/all-courses - 0.123s - Status: 200`

**Success Criteria:**
- ✅ Search results displayed ≤ 1s
- ✅ Accurate results
- ✅ No lag or delay

**Điểm Nhấn:**
- "Search rất nhanh, dưới 1 giây"
- "Backend logs cho thấy response time chính xác"
- "Có caching để tăng tốc độ"

---

### Scenario 6: Chatbot Response Time (1 phút)

**Mục tiêu:** Chứng minh AI chatbot response < 6s

**Demo Steps:**

1. **Send Query to Chatbot**
   - Ask: "Explain CPU"
   - Start timer

2. **Measure Response**
   - Wait for answer
   - Check response time
   - Verify: ≤ 6s

3. **Show Performance**
   - Open DevTools Network tab
   - Find chatbot API request
   - Show response time

**Success Criteria:**
- ✅ Response ≤ 6s
- ✅ 0 timeout errors
- ✅ Accurate answer

**Điểm Nhấn:**
- "AI response nhanh, dưới 6 giây"
- "Có error handling nếu API timeout"
- "Câu trả lời chính xác và hữu ích"

---

### Scenario 7: Performance Monitoring (2 phút)

**Mục tiêu:** Chứng minh hệ thống có monitoring

**Demo Steps:**

1. **Show Startup Logs**
   - Switch to backend terminal
   - Show startup banner:
   ```
   ✅ QA02 - PERFORMANCE:
      • Performance Monitoring - Response time tracking
      • Cache Service - In-memory cache with 5-min TTL
      • Connection Pool - Size: 10, Max Overflow: 20
   ```

2. **Show Request Logs**
   - Make some requests
   - Show logs in terminal:
   ```
   ✅ GET /api/student/courses - 0.123s - Status: 200
   ✅ POST /api/auth/login - 0.234s - Status: 200
   ```

3. **Check Health Endpoint**
   ```bash
   curl http://localhost:5000/api/monitoring/health
   ```
   - Show response:
   ```json
   {
     "status": "healthy",
     "checks": {
       "database": {"status": "healthy"}
     }
   }
   ```

4. **Check Cache Stats**
   ```bash
   curl http://localhost:5000/api/monitoring/cache-stats
   ```
   - Show response:
   ```json
   {
     "enabled": true,
     "type": "memory",
     "keys": 45
   }
   ```

**Success Criteria:**
- ✅ All requests have response time headers
- ✅ Average response time < 1s
- ✅ Slow requests are logged
- ✅ System health monitoring works

**Điểm Nhấn:**
- "Hệ thống có performance monitoring tự động"
- "Mỗi request đều được track response time"
- "Có health check endpoints để monitor"
- "Cache giúp tăng tốc độ 10x"

---

## 🔒 PHẦN 3: SECURITY (8 phút)

### Scenario 7: Signup & Data Protection (2 phút)

**Mục tiêu:** Chứng minh 100% passwords hashed

**Demo Steps:**

1. **Create New Account**
   - Go to Signup page
   - Enter details:
     - Name: Test User Demo
     - Email: testdemo@example.com
     - Password: SecurePass123!
   - Click Register

2. **Show Backend Log**
   - Switch to backend terminal
   - Show log:
   ```
   🔐 NEW USER REGISTERED: testdemo@example.com (role: student) - Password hashed with PBKDF2
   ```

3. **Verify in Database**
   - Open SQL Server Management Studio
   - Run query:
   ```sql
   SELECT TOP 1 
       Email, 
       LEFT(PasswordHash, 30) + '...' as HashedPassword,
       LEN(PasswordHash) as HashLength
   FROM Users 
   WHERE Email = 'testdemo@example.com';
   ```
   - Show result:
   ```
   Email: testdemo@example.com
   HashedPassword: pbkdf2:sha256:600000$...
   HashLength: 102
   ```

**Success Criteria:**
- ✅ 100% passwords hashed
- ✅ 0 plaintext storage
- ✅ Correct success message

**Điểm Nhấn:**
- "Password được hash bằng PBKDF2 + SHA256"
- "Không bao giờ lưu plaintext password"
- "Hash length 102 characters, rất an toàn"

---

### Scenario 8: Unauthorized Access Block (3 phút)

**Mục tiêu:** Chứng minh 100% unauthorized attempts blocked

**Demo Steps:**

1. **Login as Student**
   ```
   Email: student1@test.com
   Password: password123
   ```

2. **Attempt to Access Admin Page**
   - Manually navigate to: `/admin/users`
   - Quan sát: Access denied, redirect to dashboard

3. **Show Backend Log**
   - Switch to backend terminal
   - Show log:
   ```
   🔒 UNAUTHORIZED ACCESS BLOCKED: User 5 (role: student) attempted to access GET /api/admin/users (requires: admin)
   ```

4. **Try API Direct**
   - Open DevTools Console
   - Run:
   ```javascript
   fetch('http://localhost:5000/api/admin/users', {
     headers: {
       'Authorization': 'Bearer ' + localStorage.getItem('token')
     }
   }).then(r => r.json()).then(console.log)
   ```
   - Show response: `{error: 'forbidden'}` with status 403

5. **Check Audit Log (Optional)**
   - Login as admin
   - Go to Logs page
   - Show unauthorized attempt logged

**Success Criteria:**
- ✅ 100% unauthorized attempts blocked
- ✅ Response ≤ 2s
- ✅ No data leakage
- ✅ Events logged

**Điểm Nhấn:**
- "RBAC (Role-Based Access Control) hoạt động hoàn hảo"
- "Student không thể access admin endpoints"
- "Mọi unauthorized attempts đều được log"
- "Response 403 Forbidden, không leak data"

---

### Scenario 9: Admin Action Logging (3 phút)

**Mục tiêu:** Chứng minh 100% admin actions logged

**Demo Steps:**

1. **Login as Admin**
   ```
   Email: admin@test.com
   Password: admin123
   ```

2. **Perform Admin Actions**

   **Action 1: Update User Role**
   - Go to Users page
   - Change a user's role from Student to Teacher
   - Show backend log:
   ```
   📝 ADMIN ACTION LOGGED: Admin 1 performed 'set_role' on 'user_5' - Changed role to teacher
   ```

   **Action 2: Approve Enrollment**
   - Go to Enrollments page
   - Click "Approve" on a pending enrollment
   - Show backend log:
   ```
   📝 ADMIN ACTION LOGGED: Admin 1 performed 'approve_enrollment' on 'enroll:10' - Approved enrollment
   ```

   **Action 3: Delete User**
   - Go to Users page
   - Delete a test user
   - Show backend log:
   ```
   📝 ADMIN ACTION LOGGED: Admin 1 performed 'delete_user' on 'user_10' - Deleted user account
   ```

3. **View Audit Logs**
   - Go to Admin → Logs page
   - Show table with all logged actions:
     - LogID
     - Admin ID
     - Action
     - Target
     - Description
     - Timestamp

4. **Verify in Database**
   - Open SQL Server Management Studio
   - Run query:
   ```sql
   SELECT TOP 10 
       LogID,
       AdminID,
       Action,
       Target,
       Description,
       Timestamp
   FROM AuditLogs
   ORDER BY Timestamp DESC;
   ```
   - Show results matching the actions performed

**Success Criteria:**
- ✅ 100% admin actions logged
- ✅ 0 unauthorized changes
- ✅ Complete audit trail
- ✅ Timestamps accurate

**Điểm Nhấn:**
- "Mọi admin action đều được log tự động"
- "Có đầy đủ thông tin: who, what, when, where"
- "Audit trail không thể xóa, đảm bảo traceability"
- "Có thể export logs ra CSV/PDF"

---

## ❓ Câu Hỏi Thường Gặp

### Q1: Làm sao đảm bảo passwords an toàn?

**A:** 
- Sử dụng Werkzeug's `generate_password_hash()` với PBKDF2 + SHA256
- 600,000 iterations để chống brute-force
- Salt tự động cho mỗi password
- Không bao giờ lưu plaintext

**Demo:**
```python
# backend/app/models/user_model.py
def set_password(self, password):
    self.password_hash = generate_password_hash(password)
```

---

### Q2: RBAC hoạt động như thế nào?

**A:**
- JWT token chứa role claim
- Decorator `@require_roles()` check role
- Middleware tự động block unauthorized access
- Log mọi unauthorized attempts

**Demo:**
```python
# backend/app/services/jwt_service.py
@require_roles('admin')
def admin_only_function():
    # Only admin can access
    pass
```

---

### Q3: Performance monitoring track những gì?

**A:**
- Response time của mỗi request
- Slow requests (> 5s)
- Cache hit/miss rate
- Database connection pool status
- Health checks

**Demo:**
```python
# backend/app/middleware/performance_monitor.py
# Tự động track và log mọi request
```

---

### Q4: Cache giúp tăng performance như thế nào?

**A:**
- In-memory cache với TTL 5 phút
- Cache hit: ~0.05s (10x faster)
- Cache miss: ~0.5s (query database)
- Hit rate: 75%+

**Demo:**
```bash
# First request (cache miss)
curl http://localhost:5000/api/student/courses
# Time: ~0.5s

# Second request (cache hit)
curl http://localhost:5000/api/student/courses
# Time: ~0.05s (10x faster!)
```

---

### Q5: Pagination giúp gì cho performance?

**A:**
- Load 10 items thay vì 1000+
- Response time giảm 5-10x
- Memory usage thấp hơn
- UI mượt mà hơn

**Demo:**
- Admin Users page: Pagination với 10 users/page
- Admin Enrollments page: Pagination với 10 enrollments/page

---

## ✅ Checklist Demo

### Trước Demo
- [ ] Backend đang chạy
- [ ] Frontend đang chạy
- [ ] Database có dữ liệu test
- [ ] DevTools đã mở
- [ ] SQL Server Management Studio đã mở
- [ ] Timer/stopwatch sẵn sàng

### Trong Demo
- [ ] Scenario 1: Lesson Navigation ✅
- [ ] Scenario 2: Quiz Interaction ✅
- [ ] Scenario 3: AI Chatbot ✅
- [ ] Scenario 4: Lesson Access Speed ✅
- [ ] Scenario 5: Course Search ✅
- [ ] Scenario 6: Chatbot Response Time ✅
- [ ] Scenario 7: Signup & Data Protection ✅
- [ ] Scenario 8: Unauthorized Access Block ✅
- [ ] Scenario 9: Admin Action Logging ✅

### Sau Demo
- [ ] Trả lời câu hỏi của giảng viên
- [ ] Show thêm features nếu có thời gian
- [ ] Cảm ơn giảng viên

---

## 🎯 Tips Demo Thành Công

### 1. Chuẩn Bị Kỹ
- Test demo flow trước ít nhất 2-3 lần
- Đảm bảo mọi thứ hoạt động
- Có backup plan nếu có lỗi

### 2. Trình Bày Tự Tin
- Nói rõ ràng, không quá nhanh
- Giải thích từng bước đang làm gì
- Nhấn mạnh điểm quan trọng

### 3. Show Evidence
- Luôn show logs trong terminal
- Show database khi cần
- Show DevTools Network tab
- Show response time headers

### 4. Xử Lý Lỗi
- Nếu có lỗi, giữ bình tĩnh
- Giải thích lỗi là gì
- Show error handling của hệ thống
- Chuyển sang scenario khác

### 5. Quản Lý Thời Gian
- Usability: 5 phút
- Performance: 7 phút
- Security: 8 phút
- Q&A: 5 phút
- **Total: 25 phút**

---

## 📊 Summary Table

| # | Scenario | Time | Success Criteria | Status |
|---|----------|------|------------------|--------|
| 1 | Lesson Navigation | 2 min | ≤ 3s, clear UI | ✅ |
| 2 | Quiz Interaction | 2 min | ≤ 0.5s selection, ≤ 1s navigation | ✅ |
| 3 | AI Chatbot | 1 min | ≤ 1s input, clear UI | ✅ |
| 4 | Lesson Access | 2 min | ≤ 5s load, ≤ 4s buffer | ✅ |
| 5 | Course Search | 2 min | ≤ 1s results | ✅ |
| 6 | Chatbot Response | 1 min | ≤ 6s response | ✅ |
| 7 | Signup & Data | 2 min | 100% hashed | ✅ |
| 8 | Unauthorized Block | 3 min | 100% blocked | ✅ |
| 9 | Admin Logging | 3 min | 100% logged | ✅ |

---

**Chúc bạn demo thành công! 🎉**

**Prepared by:** E-Learning Team  
**Date:** December 6, 2024  
**Version:** 1.0
