from flask import jsonify, request
from models.course_model import Course
from models.assignment_model import Assignment
from models.enrollment_model import Enrollment
from models.report_model import Report
from models.feedback_model import Feedback
from models.activity_model import Activity
from models.user_model import User
from extensions import db
from flask_jwt_extended import get_jwt_identity
from datetime import datetime


def log_activity(student_id, content):
    activity = Activity(student_id=student_id, content=content, timestamp=datetime.utcnow())
    db.session.add(activity)
    db.session.commit()

def get_student_profile():
    student_id = get_jwt_identity()
    user = User.query.get(student_id)

    if not user:
        return jsonify({"message": "Không tìm thấy sinh viên"}), 404

    return jsonify({
        "fullname": user.fullname,
        "email": user.email,
        "class": user.class_name,  # nếu bạn có cột `class_name` trong bảng users
        "major": user.major        # nếu bạn có cột `major` trong bảng users
    }), 200

def enroll_in_course():
    data = request.get_json()
    student_id = get_jwt_identity()
    course_id = data.get("course_id")

    if not course_id:
        return jsonify({"message": "Thiếu course_id"}), 400

    existing = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
    if existing:
        return jsonify({"message": "Bạn đã đăng ký khóa học này rồi!"}), 400

    new_enrollment = Enrollment(student_id=student_id, course_id=course_id)
    db.session.add(new_enrollment)
    db.session.commit()

    log_activity(student_id, f"Đã đăng ký khóa học ID {course_id}")
    return jsonify({"message": "Đăng ký khóa học thành công!"})

def unenroll_from_course():
    data = request.get_json()
    student_id = get_jwt_identity()
    course_id = data.get("course_id")

    if not course_id:
        return jsonify({"message": "Thiếu course_id"}), 400

    enrollment = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
    if not enrollment:
        return jsonify({"message": "Bạn chưa đăng ký khóa học này."}), 404

    db.session.delete(enrollment)
    db.session.commit()

    log_activity(student_id, f"Hủy đăng ký khóa học ID {course_id}")
    return jsonify({"message": "Hủy đăng ký thành công!"})


def get_enrolled_courses():
    student_id = get_jwt_identity()
    enrollments = Enrollment.query.filter_by(student_id=student_id).all()
    course_ids = [e.course_id for e in enrollments]
    courses = Course.query.filter(Course.id.in_(course_ids)).all()

    log_activity(student_id, "Xem danh sách khóa học đã đăng ký")

    return jsonify([
        {
            "id": c.id,
            "name": c.name,
            "description": c.description
        } for c in courses
    ])


def get_assignments():
    student_id = get_jwt_identity()
    enrollments = Enrollment.query.filter_by(student_id=student_id).all()
    course_ids = [e.course_id for e in enrollments]
    assignments = Assignment.query.filter(Assignment.course_id.in_(course_ids)).all()

    log_activity(student_id, "Xem danh sách bài tập")

    return jsonify([
        {
            "id": a.id,
            "title": a.title,
            "due_date": a.due_date.strftime("%Y-%m-%d %H:%M") if a.due_date else None
        } for a in assignments
    ])


def get_progress():
    student_id = get_jwt_identity()
    reports = Report.query.filter_by(student_id=student_id).all()

    log_activity(student_id, "Xem tiến độ học tập")

    return jsonify([
        {
            "course_id": r.course_id,
            "progress_percent": r.progress_percent,
            "last_update": r.last_update.strftime("%Y-%m-%d %H:%M") if r.last_update else None
        } for r in reports
    ])


from models.feedback_model import Feedback
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from extensions import db
from datetime import datetime

def submit_feedback():
    data = request.get_json()
    student_id = get_jwt_identity()
    course_id = data.get("course_id")
    message = data.get("message")

    if not course_id or not message:
        return jsonify({"message": "Thiếu course_id hoặc nội dung đánh giá."}), 400

    feedback = Feedback(
        sender_id=student_id,
        course_id=course_id,
        message=message,
        created_at=datetime.utcnow()
    )
    db.session.add(feedback)
    db.session.commit()

    return jsonify({"message": "Gửi đánh giá thành công!"}), 200



def recent_activities():
    student_id = get_jwt_identity()
    acts = Activity.query.filter_by(student_id=student_id).order_by(Activity.timestamp.desc()).limit(5).all()

    return jsonify([
        {
            "content": a.content,
            "time": a.timestamp.strftime("%Y-%m-%d %H:%M") if a.timestamp else None
        } for a in acts
    ])


from flask_jwt_extended import get_jwt_identity
from models.user_model import User
from flask import jsonify

def get_student_profile():
    student_id = get_jwt_identity()
    user = User.query.get(student_id)

    if not user:
        return jsonify({"message": "Không tìm thấy sinh viên"}), 404

    return jsonify({
        "fullname": user.fullname,
        "email": user.email,
        "avatar_url": user.avatar_url or "",  # 👈 thêm avatar_url nếu có
        "department": user.department or "",
        "joined_date": user.joined_date.strftime("%Y-%m-%d") if user.joined_date else ""
    }), 200
