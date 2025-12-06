from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import text
from app import db
from app.models.course_model import Course
from app.models.lesson_model import Lesson
from app.models.enrollment_model import Enrollment
from app.services.cache_service import cache_get, cache_set, cache_delete_pattern


def list_all_courses_for_student():
    """
    Lists all available courses, indicating which ones the current student is enrolled in.
    Uses SQLAlchemy ORM for database queries with Redis caching.
    """
    from sqlalchemy import text
    sid = get_jwt_identity()
    
    # Try cache first
    cache_key = f"courses:student:{sid}"
    cached_data = cache_get(cache_key)
    if cached_data:
        return jsonify(cached_data)

    # Get IDs of courses the student is enrolled in
    # Use raw SQL for MSSQL to handle column name differences
    if db.get_engine().dialect.name == 'mssql':
        try:
            rows = db.session.execute(text(
                'SELECT [CourseID] FROM [dbo].[Enrollments] WHERE [UserID] = :sid'
            ), {'sid': sid}).fetchall()
            enrolled_ids = {row[0] for row in rows}
        except Exception as e:
            print(f"[Warning] Error querying enrollments: {e}")
            enrolled_ids = set()
    else:
        enrolled_courses = Enrollment.query.filter_by(student_id=sid).with_entities(Enrollment.course_id).all()
        enrolled_ids = {e[0] for e in enrolled_courses}

    # Eagerly load the teacher relationship to avoid N+1 queries
    courses = Course.query.options(db.joinedload(Course.teacher)).all()
    
    output = []
    for c in courses:
        output.append({
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "teacher_name": c.teacher.fullname if c.teacher else "N/A",
            "enrolled": c.id in enrolled_ids,
        })
    
    # Cache for 5 minutes
    cache_set(cache_key, output, ttl=300)
    
    return jsonify(output)


def enroll(course_id: int):
    """
    Enrolls the current student in a course.
    Uses SQLAlchemy ORM for database queries.
    """
    sid = int(get_jwt_identity())
    
    # Check if enrollment already exists
    exists = Enrollment.query.filter_by(student_id=sid, course_id=course_id).first()
    if exists:
        return jsonify({"message": "You are already enrolled in this course"}), 200
    
    # Create new enrollment
    new_enrollment = Enrollment(student_id=sid, course_id=course_id)
    db.session.add(new_enrollment)
    db.session.commit()
    
    return jsonify({"message": "Enrollment successful"})


def course_detail(course_id: int):
    """
    Retrieves detailed information about a specific course, including its lessons.
    Uses SQLAlchemy ORM for database queries.
    """
    # Eagerly load the teacher to avoid a separate query
    course = Course.query.options(db.joinedload(Course.teacher)).get(course_id)

    if not course:
        return jsonify({"message": "Course not found"}), 404
    
    # Get lessons for the course, ordered by their index
    lessons = Lesson.query.filter_by(course_id=course_id).order_by(Lesson.order_index).all()

    return jsonify({
        "name": course.name,
        "description": course.description,
        "category": course.category,
        "duration": course.duration,
        "teacher_id": course.teacher_id,
        "teacher_name": course.teacher.fullname if course.teacher else "N/A",
        "lessons": [{"id": l.id, "title": l.title, "content": l.content} for l in lessons]
    })


def lesson_detail(lesson_id: int):
    """
    Retrieves detailed information for a single lesson, checking for student enrollment.
    Uses SQLAlchemy ORM for database queries.
    """
    sid = get_jwt_identity()
    
    lesson = Lesson.query.get(lesson_id)
    if not lesson:
        return jsonify({"message": "Lesson not found"}), 404
        
    # Check if student is enrolled in the course this lesson belongs to
    is_enrolled = Enrollment.query.filter_by(student_id=sid, course_id=lesson.course_id).first()
    if not is_enrolled:
        return jsonify({"error": "Forbidden: not enrolled in this course"}), 403
    
    # Get course info for breadcrumb
    course = Course.query.get(lesson.course_id)
    
    # Get previous and next lesson IDs for navigation
    prev_lesson = Lesson.query.filter(
        Lesson.course_id == lesson.course_id,
        Lesson.order_index < lesson.order_index
    ).order_by(Lesson.order_index.desc()).first()
    
    next_lesson = Lesson.query.filter(
        Lesson.course_id == lesson.course_id,
        Lesson.order_index > lesson.order_index
    ).order_by(Lesson.order_index.asc()).first()
        
    return jsonify({
        "id": lesson.id,
        "title": lesson.title,
        "description": lesson.description or "",
        "content": lesson.content or "",
        "video_url": lesson.video_url or "",
        "file_url": lesson.file_url or "",
        "course_id": lesson.course_id,
        "course_title": course.name if course else "",
        "prev_lesson_id": prev_lesson.id if prev_lesson else None,
        "next_lesson_id": next_lesson.id if next_lesson else None,
    })
