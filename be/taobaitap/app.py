from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

# Cấu hình kết nối MySQL
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "your_mysql_password",
    "database": "learning_system"
}

# API: Tạo bài học mới
@app.route('/api/lessons', methods=['POST'])
def create_lesson():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    course = data.get('course')

    if not name or not description or not course:
        return jsonify({"message": "Thiếu thông tin bài học!"}), 400

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO lessons (name, description, course) VALUES (%s, %s, %s)",
            (name, description, course)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "message": "✅ Bài học đã được lưu thành công!",
            "lesson": {
                "name": name,
                "description": description,
                "course": course
            }
        }), 201
    except mysql.connector.Error as err:
        return jsonify({"message": f"Lỗi cơ sở dữ liệu: {err}"}), 500

# API: Lấy danh sách bài học
@app.route('/api/lessons', methods=['GET'])
def get_lessons():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT name, description, course FROM lessons")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        lessons = [{"name": r[0], "description": r[1], "course": r[2]} for r in rows]
        return jsonify(lessons)
    except mysql.connector.Error as err:
        return jsonify({"message": f"Lỗi: {err}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
