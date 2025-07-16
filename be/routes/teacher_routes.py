from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_cors import cross_origin
from datetime import datetime
from sqlalchemy import func

from models.enrollment_model import Enrollment
from models.course_model import Course
from models.lesson_model import Lesson
from models.assignment_model import Assignment
from models.feedback_model import Feedback
from models.report_model import Report
from models.user_model import User
from controllers.lesson_controller import add_lesson_from_file
from extensions import db

teacher_bp = Blueprint("teacher", __name__)

@teacher_bp.route("/home", methods=["GET"])
@jwt_required()
def teacher_homepage():
    teacher_id = get_jwt_identity()  # lấy từ token

    courses = db.session.query(
        Course.id,
        Course.name,
        func.count(Enrollment.student_id).label("student_count")
    ).join(Enrollment, Enrollment.course_id == Course.id, isouter=True
    ).filter(Course.teacher_id == teacher_id
    ).group_by(Course.id).all()

    result = []
    for course in courses:
        feedback = Feedback.query.filter_by(course_id=course.id).order_by(Feedback.created_at.desc()).first()
        result.append({
            "course_id": course.id,
            "name": course.name,
            "students": course.student_count,
            "feedback": feedback.message if feedback else "Chưa có góp ý"
        })

    return jsonify(result)


# Tạo khóa học
@teacher_bp.route("/courses", methods=["POST"])
@jwt_required()
def create_course():
    data = request.json
    user_id = get_jwt_identity()

    # Kiểm tra tên trùng với cùng giáo viên
    existed = Course.query.filter_by(name=data["name"], teacher_id=user_id).first()
    if existed:
        return jsonify({"message": "Tên khóa học đã tồn tại!"}), 400

    new_course = Course(
        name=data["name"],
        description=data.get("description"),
        teacher_id=int(user_id)
    )
    db.session.add(new_course)
    db.session.commit()
    return jsonify({"message": "Tạo khóa học thành công!"}), 201


# Lấy danh sách khóa học của giảng viên
@teacher_bp.route("/courses", methods=["GET"])
@jwt_required()
def list_courses():
    user_id = get_jwt_identity()
    courses = Course.query.filter_by(teacher_id=user_id).all()
    course_list = [{
        "id": c.id,
        "name": c.name,
        "description": c.description,
        "created_at": c.created_at.strftime("%Y-%m-%d %H:%M:%S") if c.created_at else None
    } for c in courses]
    return jsonify({"courses": course_list}), 200

# Cập nhật khóa học
@teacher_bp.route("/courses/<int:course_id>", methods=["PUT"])
@jwt_required()
def update_course(course_id):
    user_id = get_jwt_identity()
    course = Course.query.filter_by(id=course_id, teacher_id=user_id).first()
    if not course:
        return jsonify({"message": "Không tìm thấy khóa học!"}), 404
    data = request.json
    course.name = data.get("name", course.name)
    course.description = data.get("description", course.description)
    db.session.commit()
    return jsonify({"message": "Cập nhật khóa học thành công!"})

# Xoá khóa học
@teacher_bp.route("/courses/<int:course_id>", methods=["DELETE"])
@jwt_required()
def delete_course(course_id):
    user_id = get_jwt_identity()
    course = Course.query.filter_by(id=course_id, teacher_id=user_id).first()
    if not course:
        return jsonify({"message": "Không tìm thấy khóa học!"}), 404
    db.session.delete(course)
    db.session.commit()
    return jsonify({"message": "Xóa khóa học thành công!"})

# Chi tiết khóa học và bài học
@teacher_bp.route("/courses/<int:course_id>", methods=["GET"])
@jwt_required()
def course_detail(course_id):
    user_id = get_jwt_identity()
    course = Course.query.filter_by(id=course_id, teacher_id=user_id).first()
    if not course:
        return jsonify({"message": "Không tìm thấy khóa học"}), 404
    lessons = Lesson.query.filter_by(course_id=course.id).all()
    lesson_list = [{
        "id": l.id,
        "title": l.title,
        "content": l.content
    } for l in lessons]
    return jsonify({
        "id": course.id,
        "name": course.name,
        "description": course.description,
        "created_at": course.created_at.isoformat() if course.created_at else None,
        "lessons": lesson_list
    }), 200

# Tạo bài học
@teacher_bp.route("/lessons", methods=["POST"])
@jwt_required()
def create_lesson():
    data = request.json
    lesson = Lesson(
        title=data["title"],
        content=data["content"],
        course_id=data["course_id"]
    )
    db.session.add(lesson)
    db.session.commit()
    return jsonify({"message": "Tạo bài học thành công!"}), 201

# Upload bài học từ file
@teacher_bp.route("/upload-lesson", methods=["POST"])
@cross_origin(origins="http://127.0.0.1:5500")
@jwt_required()
def upload_lesson():
    return add_lesson_from_file()

# Tạo bài tập
@teacher_bp.route("/assignments", methods=["POST"])
@jwt_required()
def create_assignment():
    data = request.json
    try:
        assignment = Assignment(
            title=data["title"],
            description=data.get("description"),
            course_id=data["course_id"],
            deadline=datetime.fromisoformat(data["deadline"]) if "deadline" in data else None
        )
        db.session.add(assignment)
        db.session.commit()
        return jsonify({"message": "Tạo bài tập thành công!"}), 201
    except KeyError as e:
        return jsonify({"error": f"Thiếu trường bắt buộc: {str(e)}"}), 400
    except ValueError:
        return jsonify({"error": "Định dạng deadline không hợp lệ. Dùng định dạng YYYY-MM-DDTHH:MM:SS"}), 400

# Danh sách phản hồi từ sinh viên
@teacher_bp.route("/feedbacks", methods=["GET"])
@jwt_required()
def list_feedback():
    user_id = get_jwt_identity()

    feedbacks = Feedback.query.join(Course).filter(
        Course.teacher_id == user_id
    ).all()

    result = [{
        "id": f.id,
        "sender_name": f.sender.fullname if f.sender else "Không rõ",
        "course_name": f.course.name if f.course else "Không rõ",
        "message": f.message,
        "created_at": f.created_at.strftime("%Y-%m-%d %H:%M") if f.created_at else ""
    } for f in feedbacks]

    return jsonify(result), 200


# Danh sách báo cáo học tập
@teacher_bp.route("/reports", methods=["GET"])
@jwt_required()
def list_reports():
    reports = Report.query.all()
    result = [{
        "id": r.id,
        "student_id": r.student_id,
        "course_id": r.course_id,
        "progress_percent": r.progress_percent,
        "last_update": r.last_update.isoformat() if r.last_update else None
    } for r in reports]
    return jsonify(result), 200

# Hồ sơ giảng viên
@teacher_bp.route("/profile", methods=["GET"])
@jwt_required()
def teacher_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user.role != "teacher":
        return jsonify({"message": "Bạn không phải giảng viên!"}), 403
    return jsonify({
        "id": user.id,
        "fullname": user.fullname,
        "email": user.email,
        "role": user.role,
        "department": user.department,
        "joined_date": user.joined_date.isoformat() if user.joined_date else None,
        "avatar_url": user.avatar_url
    }), 200

@teacher_bp.route("/assignments", methods=["GET"])
@jwt_required()
def get_assignments_by_course():
    user_id = get_jwt_identity()
    course_id = request.args.get("course_id")
    if not course_id:
        return jsonify({"error": "Thiếu course_id"}), 400

    # Lấy tất cả assignment thuộc course đó do chính giáo viên sở hữu
    assignments = Assignment.query.join(Course).filter(
        Assignment.course_id == course_id,
        Course.teacher_id == user_id
    ).all()

    result = [{
        "id": a.id,
        "title": a.title,
        "description": a.description,
        "deadline": a.deadline.strftime("%Y-%m-%d %H:%M") if a.deadline else None,
        "course_name": a.course.name
    } for a in assignments]

    return jsonify({"assignments": result}), 200


@teacher_bp.route("/assignments/<int:assignment_id>", methods=["DELETE"])
@jwt_required()
def delete_assignment(assignment_id):
    user_id = get_jwt_identity()
    assignment = Assignment.query.get(assignment_id)

    if not assignment or assignment.course.teacher_id != user_id:
        return jsonify({"message": "Không tìm thấy hoặc không có quyền!"}), 404

    db.session.delete(assignment)
    db.session.commit()
    return jsonify({"message": "Đã xóa bài tập!"}), 200

@teacher_bp.route("/courses/<int:course_id>/details", methods=["GET"])
@jwt_required()
def course_lesson_assignment_detail(course_id):
    user_id = get_jwt_identity()

    # Kiểm tra khóa học có thuộc về giảng viên không
    course = Course.query.filter_by(id=course_id, teacher_id=user_id).first()
    if not course:
        return jsonify({"message": "Không tìm thấy khóa học"}), 404

    lessons = Lesson.query.filter_by(course_id=course_id).all()
    assignments = Assignment.query.filter_by(course_id=course_id).all()

    return jsonify({
        "course": {
            "id": course.id,
            "name": course.name,
            "description": course.description
        },
        "lessons": [{
            "id": l.id,
            "title": l.title,
            "content": l.content
        } for l in lessons],
        "assignments": [{
            "id": a.id,
            "title": a.title,
            "description": a.description,
            "deadline": a.deadline.strftime("%Y-%m-%d %H:%M") if a.deadline else None
        } for a in assignments]
    }), 200

@teacher_bp.route("/report-summary", methods=["GET"])
@jwt_required()
def report_summary():
    user_id = get_jwt_identity()

    # Lấy các khóa học của giảng viên
    teacher_courses = Course.query.filter_by(teacher_id=user_id).all()
    course_ids = [c.id for c in teacher_courses]

    if not course_ids:
        return jsonify({"message": "Không có khóa học nào!"}), 404

    # Lấy các bản ghi báo cáo học tập thuộc các khóa học
    reports = Report.query.filter(Report.course_id.in_(course_ids)).all()
    total_students = len(reports)

    if total_students == 0:
        return jsonify({
            "completion_rate": 0,
            "on_time_count": 0,
            "total_students": 0
        }), 200

    # Tính trung bình tỉ lệ hoàn thành
    avg_completion = sum(r.progress_percent for r in reports) / total_students

    # Giả sử hoàn thành đúng hạn là >= 80%
    on_time_count = sum(1 for r in reports if r.progress_percent >= 80)

    return jsonify({
        "completion_rate": round(avg_completion, 1),
        "on_time_count": on_time_count,
        "total_students": total_students
    }), 200

