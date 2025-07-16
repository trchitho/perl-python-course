from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from sqlalchemy import text

from controllers.student_controller import *
from extensions import db
from models.user_model import User
from models.course_model import Course 
from models.lesson_model import Lesson
from models.notification import Notification
from models.assignment_model import Assignment
from models.activity_model import Activity

student_bp = Blueprint("student", __name__)

@student_bp.route("/dashboard", methods=["GET", "OPTIONS"])
@cross_origin(origins="http://127.0.0.1:5501", supports_credentials=True)
def student_dashboard():
    if request.method == "OPTIONS": return '', 204
    verify_jwt_in_request()
    student_id = get_jwt_identity()

    student = User.query.get(student_id)
    if not student:
        return jsonify({"error": "Không tìm thấy sinh viên"}), 404

    enrolled_course_ids = db.session.execute(
        text("SELECT course_id FROM enrollments WHERE student_id = :sid"),
        {"sid": student_id}
    ).fetchall()
    course_ids = [row[0] for row in enrolled_course_ids]

    assignments = Assignment.query.filter(
        Assignment.course_id.in_(course_ids)
    ).order_by(Assignment.deadline.asc()).limit(3).all()

    upcoming_assignments = [{
        "title": a.title,
        "deadline": a.deadline.strftime('%d/%m')
    } for a in assignments]

    activities = Activity.query.filter_by(student_id=student_id).order_by(Activity.timestamp.desc()).limit(5).all()
    recent_activities = [{
        "detail": a.content,
        "created_at": a.timestamp.strftime("%d/%m %H:%M"),
        "type": "📌 Hoạt động"
    } for a in activities]

    return jsonify({
        "fullname": student.fullname,
        "email": student.email,
        "upcoming_assignments": upcoming_assignments,
        "recent_activities": recent_activities,
        "ai_suggestion": "Bạn nên học bài 'Vòng lặp trong Python'"
    }), 200

@student_bp.route("/enroll", methods=["POST", "OPTIONS"])
@cross_origin(origins="http://127.0.0.1:5501", supports_credentials=True)
def enroll_course():
    if request.method == "OPTIONS": return '', 204
    verify_jwt_in_request()
    return enroll_in_course()

@student_bp.route("/unenroll", methods=["POST", "OPTIONS"])
@cross_origin(origins="http://127.0.0.1:5501", supports_credentials=True)
def unenroll_course():
    if request.method == "OPTIONS": return '', 204
    verify_jwt_in_request()
    return unenroll_from_course()

@student_bp.route("/all-courses", methods=["GET", "OPTIONS"])
@cross_origin(origins="http://127.0.0.1:5501", supports_credentials=True)
def all_courses_with_enrollment_status():
    if request.method == "OPTIONS": return '', 204
    verify_jwt_in_request()
    student_id = get_jwt_identity()

    enrolled_rows = db.session.execute(
        text("SELECT course_id FROM enrollments WHERE student_id = :sid"),
        {"sid": student_id}
    ).fetchall()
    enrolled_ids = [row[0] for row in enrolled_rows]

    all_courses = Course.query.all()
    result = []
    for course in all_courses:
        teacher = User.query.get(course.teacher_id)
        result.append({
            "id": course.id,
            "name": course.name,
            "description": course.description,
            "teacher_name": teacher.fullname if teacher else "Không rõ",
            "enrolled": course.id in enrolled_ids
        })
    return jsonify(result), 200

@student_bp.route("/courses", methods=["GET", "OPTIONS"])
@cross_origin(origins="http://127.0.0.1:5501", supports_credentials=True)
def view_enrolled_courses():
    if request.method == "OPTIONS": return '', 204
    verify_jwt_in_request()
    return get_enrolled_courses()

@student_bp.route("/course-detail/<int:course_id>", methods=["GET", "OPTIONS"])
@cross_origin(origins="http://127.0.0.1:5501", supports_credentials=True)
def get_course_detail(course_id):
    if request.method == "OPTIONS": return '', 204
    verify_jwt_in_request()
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"message": "Không tìm thấy khóa học"}), 404

    lessons = Lesson.query.filter_by(course_id=course_id).all()
    lesson_data = [
        {
            "id": lesson.id,
            "title": lesson.title,
            "content": lesson.content
        } for lesson in lessons
    ]

    return jsonify({
        "name": course.name,
        "description": course.description,
        "lessons": lesson_data
    }), 200

@student_bp.route("/lesson/<int:lesson_id>", methods=["GET", "OPTIONS"])
@cross_origin(origins="http://127.0.0.1:5501", supports_credentials=True)
def get_lesson_detail(lesson_id):
    if request.method == "OPTIONS": return '', 204
    verify_jwt_in_request()
    lesson = Lesson.query.get(lesson_id)
    if not lesson:
        return jsonify({"message": "Không tìm thấy bài học"}), 404

    return jsonify({
        "id": lesson.id,
        "title": lesson.title,
        "content": lesson.content,
        "quiz": lesson.quiz
    }), 200

@student_bp.route("/assignments", methods=["GET", "OPTIONS"])
@cross_origin(origins="http://127.0.0.1:5501", supports_credentials=True)
def view_assignments():
    if request.method == "OPTIONS": return '', 204
    verify_jwt_in_request()
    student_id = get_jwt_identity()

    enrolled_course_ids = db.session.execute(
        text("SELECT course_id FROM enrollments WHERE student_id = :sid"),
        {"sid": student_id}
    ).fetchall()
    course_ids = [row[0] for row in enrolled_course_ids]

    assignments = Assignment.query.filter(Assignment.course_id.in_(course_ids)).all()
    result = []
    for a in assignments:
        course = Course.query.get(a.course_id)
        result.append({
            "id": a.id,
            "title": a.title,
            "description": a.description,
            "deadline": a.deadline.isoformat() if a.deadline else None,
            "course_id": a.course_id,
            "course_name": course.name if course else "Không rõ"
        })
    return jsonify(result), 200

@student_bp.route("/progress", methods=["GET", "OPTIONS"])
@cross_origin(origins="http://127.0.0.1:5501", supports_credentials=True)
def view_progress():
    if request.method == "OPTIONS": return '', 204
    verify_jwt_in_request()
    return get_progress()

@student_bp.route("/feedback", methods=["POST", "OPTIONS"])
@cross_origin(origins="http://127.0.0.1:5501", supports_credentials=True)
def post_feedback():
    if request.method == "OPTIONS": return '', 204
    verify_jwt_in_request()
    return submit_feedback()

@student_bp.route("/activities", methods=["GET", "OPTIONS"])
@cross_origin(origins="http://127.0.0.1:5501", supports_credentials=True)
def view_activities():
    if request.method == "OPTIONS": return '', 204
    verify_jwt_in_request()
    return recent_activities()

@student_bp.route("/profile", methods=["GET", "OPTIONS"])
@cross_origin(origins="http://127.0.0.1:5501", supports_credentials=True)
def student_profile():
    if request.method == "OPTIONS": return '', 204
    verify_jwt_in_request()
    return get_student_profile()

@student_bp.route("/notifications", methods=["GET"])
@cross_origin(origins="http://127.0.0.1:5501", supports_credentials=True)
def get_notifications():
    verify_jwt_in_request()
    current_user_id = get_jwt_identity()
    notifications = Notification.query.filter_by(student_id=current_user_id).order_by(Notification.created_at.desc()).all()

    return jsonify([
        {
            "id": n.id,
            "content": n.content,
            "created_at": n.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for n in notifications
    ])
