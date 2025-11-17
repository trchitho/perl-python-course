from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from app import db
from sqlalchemy import text
from app.models.course_model import Course
from app.models.lesson_model import Lesson
from app.models.enrollment_model import Enrollment


def list_all_courses_for_student():
    sid = get_jwt_identity()
    # Handle MSSQL schema names (Enrollments with UserID/CourseID) vs generic
    dialect = db.get_engine().dialect.name
    if dialect == 'mssql':
        # Real SQL Server schema
        sql = text("SELECT [CourseID] FROM [dbo].[Enrollments] WHERE [UserID] = :sid")
        rows = db.session.execute(sql, {"sid": sid}).fetchall()
        enrolled_ids = [r[0] for r in rows]
        # Fetch courses from MSSQL table
        c_rows = db.session.execute(text(
            "SELECT [CourseID], [Title], [Description], [TeacherID], [Status] FROM [dbo].[Courses]"
        )).fetchall()
        out = []
        for r in c_rows:
            out.append({
                "id": r[0],
                "name": r[1],
                "description": r[2],
                "teacher_name": "",
                "enrolled": r[0] in enrolled_ids,
            })
        return jsonify(out)
    else:
        rows = db.session.execute(text("SELECT course_id FROM enrollments WHERE student_id = :sid"), {"sid": sid}).fetchall()
        enrolled_ids = [r[0] for r in rows]
        courses = Course.query.all()
        out = []
        for c in courses:
            out.append({
                "id": c.id,
                "name": c.name,
                "description": c.description,
                "teacher_name": "",
                "enrolled": c.id in enrolled_ids,
            })
        return jsonify(out)


def enroll(course_id: int):
    sid = int(get_jwt_identity())
    # MSSQL schema uses [dbo].[Enrollments] with UserID/CourseID and defaults for Status/PaymentStatus/EnrolledDate
    if db.get_engine().dialect.name == 'mssql':
        exists = db.session.execute(
            text('SELECT 1 FROM [dbo].[Enrollments] WHERE [UserID]=:uid AND [CourseID]=:cid'),
            { 'uid': sid, 'cid': course_id }
        ).fetchone()
        if exists:
            return jsonify({"message": "You are already enrolled in this course"}), 200
        db.session.execute(
            text('INSERT INTO [dbo].[Enrollments] ([UserID],[CourseID]) VALUES (:uid,:cid)'),
            { 'uid': sid, 'cid': course_id }
        )
        db.session.commit()
        return jsonify({"message": "Enrollment successful"})

    # Generic ORM path
    exists = Enrollment.query.filter_by(student_id=sid, course_id=course_id).first()
    if exists:
        return jsonify({"message": "You are already enrolled in this course"}), 200
    db.session.add(Enrollment(student_id=sid, course_id=course_id))
    db.session.commit()
    return jsonify({"message": "Enrollment successful"})


def course_detail(course_id: int):
    if db.get_engine().dialect.name == 'mssql':
        row = db.session.execute(text(
            'SELECT c.[Title], c.[Description], c.[Category], c.[Duration], c.[TeacherID], u.[FullName] '
            'FROM [dbo].[Courses] c '
            'LEFT JOIN [dbo].[Users] u ON u.[UserID] = c.[TeacherID] '
            'WHERE c.[CourseID] = :id'
        ), {'id': course_id}).fetchone()
        if not row:
            return jsonify({"message": "Course not found"}), 404
        # Fetch lessons from MSSQL schema
        lrows = db.session.execute(text(
            'SELECT [LessonID], [Title], [Description] FROM [dbo].[Lessons] WHERE [CourseID]=:id ORDER BY [OrderIndex], [LessonID]'
        ), {'id': course_id}).fetchall()
        return jsonify({
            "name": row[0],
            "description": row[1],
            "category": row[2],
            "duration": row[3],
            "teacher_id": row[4],
            "teacher_name": row[5],
            "lessons": [{"id": r[0], "title": r[1], "content": r[2]} for r in lrows]
        })
    c = Course.query.get(course_id)
    if not c:
        return jsonify({"message": "Course not found"}), 404
    lessons = Lesson.query.filter_by(course_id=course_id).all()
    return jsonify({
        "name": c.name,
        "description": c.description,
        "lessons": [{"id": l.id, "title": l.title, "content": l.content} for l in lessons]
    })


def lesson_detail(lesson_id: int):
    dialect = db.get_engine().dialect.name
    sid = get_jwt_identity()
    if dialect == 'mssql':
        # Try common casing variants for the video column
        row = None
        video_idx = 4
        content_idx = 5
        try:
            row = db.session.execute(text(
                "SELECT [LessonID],[CourseID],[Title],[Description],[VideoUrl],[Content] FROM [dbo].[Lessons] WHERE [LessonID]=:id"
            ), { 'id': lesson_id }).fetchone()
        except Exception:
            try:
                row = db.session.execute(text(
                    "SELECT [LessonID],[CourseID],[Title],[Description],[VideoURL],[Content] FROM [dbo].[Lessons] WHERE [LessonID]=:id"
                ), { 'id': lesson_id }).fetchone()
            except Exception:
                row = db.session.execute(text(
                    "SELECT [LessonID],[CourseID],[Title],[Description], NULL as [Video], NULL as [Content] FROM [dbo].[Lessons] WHERE [LessonID]=:id"
                ), { 'id': lesson_id }).fetchone()
        if not row:
            return jsonify({"message": "Lesson not found"}), 404
        # enrollment check
        ok = db.session.execute(text(
            "SELECT 1 FROM [dbo].[Enrollments] WHERE [UserID]=:uid AND [CourseID]=:cid"
        ), { 'uid': sid, 'cid': row[1] }).fetchone()
        if not ok:
            return jsonify({"error": "Forbidden: not enrolled in this course"}), 403
        return jsonify({
            "id": row[0],
            "title": row[2],
            "content": (row[content_idx] if len(row) > content_idx else None) or row[3],
            "quiz": None,
            "video_url": (row[video_idx] if len(row) > video_idx else None) or "",
        })
    # generic
    l = Lesson.query.get(lesson_id)
    if not l:
        return jsonify({"message": "Lesson not found"}), 404
    ok = Enrollment.query.filter_by(student_id=sid, course_id=l.course_id).first()
    if not ok:
        return jsonify({"error": "Forbidden: not enrolled in this course"}), 403
    return jsonify({
        "id": l.id,
        "title": l.title,
        "content": l.content,
        "quiz": l.quiz,
        "video_url": l.video_url or "",
    })
