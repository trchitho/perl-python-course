-- Placement Test Questions
-- IT Knowledge Assessment Questions

-- Create PlacementTestQuestions table if not exists
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'PlacementTestQuestions')
BEGIN
    CREATE TABLE PlacementTestQuestions (
        QuestionID INT PRIMARY KEY IDENTITY(1,1),
        QuestionText NVARCHAR(MAX) NOT NULL,
        OptionA NVARCHAR(500) NOT NULL,
        OptionB NVARCHAR(500) NOT NULL,
        OptionC NVARCHAR(500) NOT NULL,
        OptionD NVARCHAR(500) NOT NULL,
        CorrectAnswer CHAR(1) NOT NULL CHECK (CorrectAnswer IN ('A','B','C','D')),
        Difficulty VARCHAR(20) NOT NULL CHECK (Difficulty IN ('Beginner','Intermediate','Advanced')),
        Category VARCHAR(50) NOT NULL,
        Points INT NOT NULL DEFAULT 1
    );
END
GO

-- Clear existing questions
DELETE FROM PlacementTestQuestions;
GO

-- Insert Beginner Questions (1 point each)
INSERT INTO PlacementTestQuestions (QuestionText, OptionA, OptionB, OptionC, OptionD, CorrectAnswer, Difficulty, Category, Points) VALUES
(N'CPU là viết tắt của gì?', N'Central Processing Unit', N'Computer Personal Unit', N'Central Program Utility', N'Computer Processing Unit', 'A', 'Beginner', 'Hardware', 1),
(N'RAM là loại bộ nhớ gì?', N'Bộ nhớ cố định', N'Bộ nhớ tạm thời', N'Bộ nhớ ngoài', N'Bộ nhớ cache', 'B', 'Beginner', 'Hardware', 1),
(N'Đơn vị đo dung lượng lưu trữ nhỏ nhất là gì?', N'Byte', N'Bit', N'Kilobyte', N'Megabyte', 'B', 'Beginner', 'Basics', 1),
(N'Hệ điều hành nào sau đây là của Microsoft?', N'macOS', N'Linux', N'Windows', N'Android', 'C', 'Beginner', 'Software', 1),
(N'HTML là viết tắt của gì?', N'HyperText Markup Language', N'High Tech Modern Language', N'Home Tool Markup Language', N'Hyperlinks and Text Markup Language', 'A', 'Beginner', 'Web', 1),
(N'Phần mềm nào dùng để duyệt web?', N'Microsoft Word', N'Google Chrome', N'Adobe Photoshop', N'VLC Media Player', 'B', 'Beginner', 'Software', 1),
(N'Phím tắt Ctrl+C dùng để làm gì?', N'Cắt văn bản', N'Sao chép văn bản', N'Dán văn bản', N'Xóa văn bản', 'B', 'Beginner', 'Basics', 1),
(N'File có đuôi .docx là file gì?', N'Hình ảnh', N'Video', N'Văn bản Word', N'Âm thanh', 'C', 'Beginner', 'Software', 1),
(N'WWW là viết tắt của gì?', N'World Wide Web', N'World Web Wide', N'Wide World Web', N'Web World Wide', 'A', 'Beginner', 'Web', 1),
(N'Email là gì?', N'Thư điện tử', N'Trang web', N'Phần mềm', N'Thiết bị phần cứng', 'A', 'Beginner', 'Internet', 1);

-- Insert Intermediate Questions (2 points each)
INSERT INTO PlacementTestQuestions (QuestionText, OptionA, OptionB, OptionC, OptionD, CorrectAnswer, Difficulty, Category, Points) VALUES
(N'CSS được dùng để làm gì?', N'Tạo cấu trúc trang web', N'Tạo giao diện và định dạng trang web', N'Lập trình logic', N'Quản lý database', 'B', 'Intermediate', 'Web', 2),
(N'JavaScript chạy ở đâu?', N'Chỉ trên server', N'Chỉ trên browser', N'Cả browser và server', N'Chỉ trên mobile', 'C', 'Intermediate', 'Programming', 2),
(N'SQL được dùng để làm gì?', N'Thiết kế giao diện', N'Quản lý và truy vấn database', N'Tạo animation', N'Xử lý hình ảnh', 'B', 'Intermediate', 'Database', 2),
(N'Git là gì?', N'Ngôn ngữ lập trình', N'Hệ quản trị database', N'Hệ thống quản lý phiên bản', N'Framework web', 'C', 'Intermediate', 'Tools', 2),
(N'API là viết tắt của gì?', N'Application Programming Interface', N'Advanced Programming Integration', N'Automated Program Interaction', N'Application Process Integration', 'A', 'Intermediate', 'Programming', 2),
(N'HTTP status code 404 có nghĩa là gì?', N'Server error', N'Not Found', N'Unauthorized', N'Success', 'B', 'Intermediate', 'Web', 2),
(N'JSON được dùng để làm gì?', N'Định dạng và trao đổi dữ liệu', N'Tạo giao diện', N'Viết code', N'Quản lý file', 'A', 'Intermediate', 'Programming', 2),
(N'Framework là gì?', N'Ngôn ngữ lập trình', N'Khung làm việc có sẵn các công cụ', N'Database', N'Hệ điều hành', 'B', 'Intermediate', 'Programming', 2),
(N'Cloud computing là gì?', N'Lưu trữ trên máy tính cá nhân', N'Lưu trữ và xử lý dữ liệu trên internet', N'Lưu trữ trên USB', N'Lưu trữ trên CD', 'B', 'Intermediate', 'Cloud', 2),
(N'Responsive design là gì?', N'Thiết kế nhanh', N'Thiết kế tự động', N'Thiết kế thích ứng với nhiều kích thước màn hình', N'Thiết kế đơn giản', 'C', 'Intermediate', 'Web', 2);

-- Insert Advanced Questions (3 points each)
INSERT INTO PlacementTestQuestions (QuestionText, OptionA, OptionB, OptionC, OptionD, CorrectAnswer, Difficulty, Category, Points) VALUES
(N'RESTful API sử dụng HTTP method nào để lấy dữ liệu?', N'POST', N'GET', N'PUT', N'DELETE', 'B', 'Advanced', 'API', 3),
(N'Trong OOP, Polymorphism là gì?', N'Kế thừa', N'Đóng gói', N'Đa hình', N'Trừu tượng', 'C', 'Advanced', 'Programming', 3),
(N'Docker được dùng để làm gì?', N'Viết code', N'Container hóa ứng dụng', N'Thiết kế database', N'Tạo giao diện', 'B', 'Advanced', 'DevOps', 3),
(N'Trong database, Index được dùng để làm gì?', N'Tăng tốc độ truy vấn', N'Lưu trữ dữ liệu', N'Xóa dữ liệu', N'Backup dữ liệu', 'A', 'Advanced', 'Database', 3),
(N'JWT là viết tắt của gì?', N'Java Web Token', N'JSON Web Token', N'JavaScript Web Tool', N'Java Web Tool', 'B', 'Advanced', 'Security', 3),
(N'Microservices architecture là gì?', N'Kiến trúc ứng dụng nhỏ', N'Kiến trúc chia ứng dụng thành các service độc lập', N'Kiến trúc đơn giản', N'Kiến trúc cũ', 'B', 'Advanced', 'Architecture', 3),
(N'Redis thường được dùng làm gì?', N'Database chính', N'Cache và message broker', N'Web server', N'File storage', 'B', 'Advanced', 'Database', 3),
(N'CI/CD là viết tắt của gì?', N'Code Integration/Code Deployment', N'Continuous Integration/Continuous Deployment', N'Computer Integration/Computer Deployment', N'Code Inspection/Code Development', 'B', 'Advanced', 'DevOps', 3),
(N'WebSocket khác gì so với HTTP?', N'Không có khác biệt', N'WebSocket cho phép giao tiếp 2 chiều real-time', N'WebSocket chậm hơn', N'WebSocket chỉ dùng cho mobile', 'B', 'Advanced', 'Web', 3),
(N'Trong Git, merge conflict xảy ra khi nào?', N'Khi tạo branch mới', N'Khi có thay đổi xung đột giữa các branch', N'Khi commit code', N'Khi push code', 'B', 'Advanced', 'Tools', 3);

GO

-- Verify data
SELECT 
    Difficulty,
    COUNT(*) as QuestionCount,
    SUM(Points) as TotalPoints
FROM PlacementTestQuestions
GROUP BY Difficulty
ORDER BY 
    CASE Difficulty
        WHEN 'Beginner' THEN 1
        WHEN 'Intermediate' THEN 2
        WHEN 'Advanced' THEN 3
    END;

PRINT 'Placement test questions inserted successfully!';
PRINT 'Total questions: 30 (10 Beginner, 10 Intermediate, 10 Advanced)';
PRINT 'Total possible points: 60';
