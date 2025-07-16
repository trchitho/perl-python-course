from models.course_model import Course
from flask import jsonify

def get_courses_by_teacher(teacher_id):
    courses = Course.query.filter_by(teacher_id=teacher_id).all()
    course_list = []
    for c in courses:
        course_list.append({
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "created_at": c.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    return jsonify({"courses": course_list})
