from flask import jsonify
from sqlalchemy import text
from flask_jwt_extended import get_jwt_identity
from app import db
from app.models.announcement_model import Announcement
from app.models.course_model import Course


def teacher_create_announcement(data):
    teacher_id = int(get_jwt_identity())
    course_id = data.get('course_id')
    title = (data.get('title') or '').strip()
    message = (data.get('message') or '').strip()
    if not course_id or not message:
        return jsonify({'message': 'Missing course_id or message'}), 400

    if db.get_engine().dialect.name == 'mssql':
        # Verify ownership
        row = db.session.execute(text('SELECT TeacherID FROM Courses WHERE CourseID=:id'), {'id': course_id}).fetchone()
        if not row or (row[0] and int(row[0]) != teacher_id):
            return jsonify({'message': 'Forbidden or not found'}), 403
        r = db.session.execute(text(
            'INSERT INTO Announcements(CourseID,TeacherID,Title,Message,CreatedAt) OUTPUT INSERTED.AnnouncementID VALUES(:cid,:tid,:t,:m,GETDATE())'
        ), {'cid': course_id, 'tid': teacher_id, 't': title or None, 'm': message}).fetchone()
        db.session.commit()
        return jsonify({'message': 'Announcement created', 'id': int(r[0])}), 201

    # generic ORM
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'message': 'Course not found'}), 404
    if course.teacher_id and int(course.teacher_id) != teacher_id:
        return jsonify({'message': 'Forbidden: you do not own this course'}), 403

    ann = Announcement(course_id=course_id, teacher_id=teacher_id, title=title or None, message=message)
    db.session.add(ann)
    db.session.commit()
    return jsonify({'message': 'Announcement created', 'id': ann.id}), 201


def teacher_list_announcements(course_id=None):
    teacher_id = int(get_jwt_identity())
    params = {'tid': teacher_id}
    course_clause = ""
    if course_id:
        params['cid'] = course_id
        course_clause = "AND a.CourseID = :cid" if db.get_engine().dialect.name == 'mssql' else "AND a.course_id = :cid"

    if db.get_engine().dialect.name == 'mssql':
        sql = text(
            f"""
            SELECT a.[AnnouncementID], a.[CourseID], c.[Title] AS CourseTitle,
                   a.[Title], a.[Message], a.[CreatedAt]
            FROM [dbo].[Announcements] a
            JOIN [dbo].[Courses] c ON c.[CourseID] = a.[CourseID]
            WHERE c.[TeacherID] = :tid {course_clause}
            ORDER BY a.[CreatedAt] DESC
            """
        )
        rows = db.session.execute(sql, params).fetchall()
        return jsonify([{
            'id': r[0],
            'course_id': r[1],
            'course_name': r[2] or '',
            'title': r[3] or '',
            'message': r[4],
            'created_at': str(r[5]) if r[5] else ''
        } for r in rows])

    sql = text(
        f"""
        SELECT a.id, a.course_id, c.name AS course_name,
               a.title, a.message, a.created_at
        FROM announcements a
        JOIN courses c ON c.id = a.course_id
        WHERE c.teacher_id = :tid {course_clause}
        ORDER BY a.created_at DESC
        """
    )
    rows = db.session.execute(sql, params).fetchall()
    out = []
    for r in rows:
        out.append({
            'id': r[0],
            'course_id': r[1],
            'course_name': r[2] or '',
            'title': r[3] or '',
            'message': r[4],
            'created_at': r[5].strftime('%Y-%m-%d %H:%M') if getattr(r[5], 'strftime', None) else (str(r[5]) if r[5] else '')
        })
    return jsonify(out)


def student_list_announcements(course_id=None):
    student_id = int(get_jwt_identity())
    # MSSQL vs generic schema handling
    dialect = db.get_engine().dialect.name
    params = {'sid': student_id}
    if course_id:
        params['cid'] = course_id
    rows = []
    if dialect == 'mssql':
        # Try SQL Server-style names first
        try:
            sql = text(
                """
                SELECT a.[AnnouncementID], a.[CourseID], c.[Title] AS CourseTitle,
                       a.[Title], a.[Message], a.[CreatedAt], u.[FullName] AS TeacherName
                FROM [dbo].[Announcements] a
                JOIN [dbo].[Courses] c ON c.[CourseID] = a.[CourseID]
                LEFT JOIN [dbo].[Users] u ON u.[UserID] = c.[TeacherID]
                JOIN [dbo].[Enrollments] e ON e.[CourseID] = a.[CourseID]
                WHERE e.[UserID] = :sid
                {course_clause}
                ORDER BY a.[CreatedAt] DESC
                """.format(course_clause="AND a.[CourseID] = :cid" if course_id else "")
            )
            rows = db.session.execute(sql, params).fetchall()
        except Exception:
            # Fallback to lowercase snake case tables if they exist
            sql = text(
                """
                SELECT a.id, a.course_id, c.name AS course_name,
                       a.title, a.message, a.created_at, u.fullname AS teacher_name
                FROM announcements a
                JOIN courses c ON c.id = a.course_id
                LEFT JOIN users u ON u.id = c.teacher_id
                JOIN enrollments e ON e.course_id = a.course_id
                WHERE e.student_id = :sid
                {course_clause}
                ORDER BY a.created_at DESC
                """.format(course_clause="AND a.course_id = :cid" if course_id else "")
            )
            rows = db.session.execute(sql, params).fetchall()
    else:
        sql = text(
            """
            SELECT a.id, a.course_id, c.name AS course_name,
                   a.title, a.message, a.created_at, u.fullname AS teacher_name
            FROM announcements a
            JOIN courses c ON c.id = a.course_id
            LEFT JOIN users u ON u.id = c.teacher_id
            JOIN enrollments e ON e.course_id = a.course_id
            WHERE e.student_id = :sid
            {course_clause}
            ORDER BY a.created_at DESC
            """.format(course_clause="AND a.course_id = :cid" if course_id else "")
        )
        rows = db.session.execute(sql, params).fetchall()

    out = []
    for r in rows:
        # Handle either column naming set
        rid, rcid, rcourse, rtitle, rmsg, rcreated, rteacher = r[0], r[1], r[2], r[3], r[4], r[5], r[6]
        out.append({
            'id': rid, 'course_id': rcid, 'title': rtitle or '', 'message': rmsg,
            'created_at': rcreated.strftime('%Y-%m-%d %H:%M') if getattr(rcreated, 'strftime', None) else (str(rcreated) if rcreated else ''),
            'course_name': rcourse or '',
            'teacher_name': rteacher or ''
        })
    return jsonify(out)
