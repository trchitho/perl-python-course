from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import text
from app import db
from app.models.course_model import Course
from app.models.lesson_model import Lesson
from app.models.quiz_model import Quiz, QuizResult
from app.models.enrollment_model import Enrollment


def stats_for_teacher():
    tid = int(get_jwt_identity())
    if db.get_engine().dialect.name == 'mssql':
        courses = db.session.execute(text('SELECT COUNT(*) FROM [dbo].[Courses] WHERE TeacherID = :tid'), {'tid': tid}).scalar() or 0
        students = db.session.execute(text(
            """
            SELECT COUNT(DISTINCT e.UserID) FROM [dbo].[Enrollments] e
            WHERE e.CourseID IN (SELECT CourseID FROM [dbo].[Courses] WHERE TeacherID = :tid)
            """
        ), {'tid': tid}).scalar() or 0
        quizzes = db.session.execute(text(
            """
            SELECT COUNT(*) FROM [dbo].[Quizzes] q
            WHERE q.CourseID IN (SELECT CourseID FROM [dbo].[Courses] WHERE TeacherID = :tid)
            """
        ), {'tid': tid}).scalar() or 0
        avg_row = db.session.execute(text(
            """
            SELECT AVG(r.Score) FROM [dbo].[QuizResults] r
            WHERE r.QuizID IN (
              SELECT q.QuizID FROM [dbo].[Quizzes] q WHERE q.CourseID IN (SELECT CourseID FROM [dbo].[Courses] WHERE TeacherID = :tid)
            )
            """
        ), {'tid': tid}).fetchone()
        avg = float(avg_row[0]) if avg_row and avg_row[0] is not None else 0.0
    else:
        courses = Course.query.filter_by(teacher_id=tid).count()
        rows = db.session.execute(text(
            "SELECT COUNT(DISTINCT e.student_id) FROM enrollments e JOIN courses c ON c.id=e.course_id WHERE c.teacher_id=:tid"
        ), {'tid': tid}).fetchone()
        students = rows[0] if rows else 0
        quizzes = db.session.execute(text(
            "SELECT COUNT(*) FROM quizzes q JOIN courses c ON c.id=q.course_id WHERE c.teacher_id=:tid"
        ), {'tid': tid}).scalar() or 0
        avg_row = db.session.execute(text(
            "SELECT AVG(r.score) FROM quiz_results r JOIN quizzes q ON q.id=r.quiz_id JOIN courses c ON c.id=q.course_id WHERE c.teacher_id=:tid"
        ), {'tid': tid}).fetchone()
        avg = float(avg_row[0]) if avg_row and avg_row[0] is not None else 0.0
    return jsonify({'courses': int(courses), 'students': int(students), 'quizzes': int(quizzes), 'avg_score': round(avg, 2)})


def list_all_quizzes_for_teacher():
    tid = int(get_jwt_identity())
    if db.get_engine().dialect.name == 'mssql':
        rows = db.session.execute(text(
            """
            SELECT q.[QuizID], q.[CourseID], q.[Title], q.[Description], q.[TimeLimit], q.[CreatedAt],\r\n                   (SELECT COUNT(*) FROM [dbo].[QuizQuestions] qq WHERE qq.[QuizID]=q.[QuizID]) AS QCount,\r\n                   c.[Title] AS CourseTitle
            FROM [dbo].[Quizzes] q\r\n            JOIN [dbo].[Courses] c ON c.[CourseID] = q.[CourseID]\r\n            WHERE c.[TeacherID] = :tid\r\n            ORDER BY q.[QuizID] DESC
            """
        ), {'tid': tid}).fetchall()
        return jsonify([{ 'id': r[0], 'course_id': r[1], 'title': r[2], 'description': r[3], 'time_limit': r[4], 'created_at': str(r[5]) if r[5] else '', 'total_questions': int(r[6] or 0), 'course_name': r[7] } for r in rows])
    # generic SQL
    rows = db.session.execute(text(
        """
        SELECT q.id, q.course_id, q.title, q.description, q.time_limit, q.created_at, c.name\r\n        FROM quizzes q\r\n        JOIN courses c ON c.id = q.course_id\r\n        WHERE c.teacher_id = :tid
        ORDER BY q.id DESC
        """
    ), {'tid': tid}).fetchall()
    out = []
    for r in rows:
        cnt = db.session.execute(text('SELECT COUNT(*) FROM quiz_questions WHERE quiz_id=:id'), {'id': r[0]}).scalar() or 0
        out.append({ 'id': r[0], 'course_id': r[1], 'title': r[2], 'description': r[3], 'time_limit': r[4], 'created_at': str(r[5]) if r[5] else '', 'total_questions': int(cnt), 'course_name': r[6] })
    return jsonify(out)


def list_courses():
    tid = int(get_jwt_identity())
    if db.get_engine().dialect.name == 'mssql':
        rows = db.session.execute(text(
            "SELECT CourseID, Title, Description, Status FROM Courses WHERE TeacherID=:tid ORDER BY CourseID DESC"
        ), {'tid': tid}).fetchall()
        return jsonify([{ 'id': r[0], 'name': r[1], 'description': r[2], 'status': r[3] or 'draft' } for r in rows])
    cs = Course.query.filter_by(teacher_id=tid).order_by(Course.id.desc()).all()
    return jsonify([{ 'id': c.id, 'name': c.name, 'description': c.description, 'status': c.status or 'draft' } for c in cs])


def create_course(data: dict):
    tid = int(get_jwt_identity())
    if db.get_engine().dialect.name == 'mssql':
        r = db.session.execute(text(
            """
            INSERT INTO Courses(Title, Description, Category, Duration, TeacherID, Status)
            OUTPUT INSERTED.CourseID
            VALUES(:t, :d, :c, :dur, :tid, :st)
            """
        ), {'t': data.get('name') or data.get('title') or 'Untitled', 'd': data.get('description'), 'c': data.get('category'), 'dur': data.get('duration'), 'tid': tid, 'st': data.get('status') or 'draft'}).fetchone()
        db.session.commit()
        return jsonify({'message': 'created', 'id': int(r[0])})
    c = Course(name=data.get('name') or data.get('title') or 'Untitled', description=data.get('description'), category=data.get('category'), duration=data.get('duration'), teacher_id=tid, status=data.get('status') or 'draft')
    db.session.add(c)
    db.session.commit()
    return jsonify({'message': 'created', 'id': c.id})


def update_course(course_id: int, data: dict):
    tid = int(get_jwt_identity())
    if db.get_engine().dialect.name == 'mssql':
        # verify ownership
        row = db.session.execute(text('SELECT TeacherID FROM Courses WHERE CourseID=:id'), {'id': course_id}).fetchone()
        if not row or (row[0] and int(row[0]) != tid):
            return jsonify({'error': 'not found'}), 404
        db.session.execute(text('UPDATE Courses SET Title=:t, Description=:d, Category=:c, Duration=:dur WHERE CourseID=:id'),
                           {'t': data.get('name') or data.get('title'), 'd': data.get('description'), 'c': data.get('category'), 'dur': data.get('duration'), 'id': course_id})
        db.session.commit()
        return jsonify({'message': 'updated'})
    c = Course.query.get(course_id)
    if not c or (c.teacher_id and c.teacher_id != tid):
        return jsonify({'error': 'not found'}), 404
    for k in ('name','description','category','duration'):
        if k in data: setattr(c, k, data[k])
    db.session.add(c)
    db.session.commit()
    return jsonify({'message': 'updated'})


def delete_course(course_id: int):
    tid = int(get_jwt_identity())
    if db.get_engine().dialect.name == 'mssql':
        row = db.session.execute(text('SELECT TeacherID FROM Courses WHERE CourseID=:id'), {'id': course_id}).fetchone()
        if not row or (row[0] and int(row[0]) != tid):
            return jsonify({'error': 'not found'}), 404
        db.session.execute(text('DELETE FROM Courses WHERE CourseID=:id'), {'id': course_id})
        db.session.commit()
        return jsonify({'message': 'deleted'})
    c = Course.query.get(course_id)
    if not c or (c.teacher_id and c.teacher_id != tid):
        return jsonify({'error': 'not found'}), 404
    db.session.delete(c)
    db.session.commit()
    return jsonify({'message': 'deleted'})


def toggle_course_status(course_id: int, status: str):
    tid = int(get_jwt_identity())
    if db.get_engine().dialect.name == 'mssql':
        row = db.session.execute(text('SELECT TeacherID FROM Courses WHERE CourseID=:id'), {'id': course_id}).fetchone()
        if not row or (row[0] and int(row[0]) != tid):
            return jsonify({'error': 'not found'}), 404
        db.session.execute(text('UPDATE Courses SET Status=:s WHERE CourseID=:id'), {'s': status, 'id': course_id})
        db.session.commit()
        return jsonify({'message': 'status updated'})
    c = Course.query.get(course_id)
    if not c or (c.teacher_id and c.teacher_id != tid):
        return jsonify({'error': 'not found'}), 404
    c.status = status
    db.session.add(c)
    db.session.commit()
    return jsonify({'message': 'status updated'})


def list_lessons(course_id: int):
    tid = int(get_jwt_identity())
    if db.get_engine().dialect.name == 'mssql':
        # verify ownership
        row = db.session.execute(text('SELECT TeacherID FROM Courses WHERE CourseID=:id'), {'id': course_id}).fetchone()
        if not row or (row[0] and int(row[0]) != tid):
            return jsonify({'error': 'not found'}), 404
        try:
            ls = db.session.execute(text(
                'SELECT LessonID, Title, Description, VideoUrl, OrderIndex, Content FROM Lessons WHERE CourseID=:id ORDER BY OrderIndex, LessonID'
            ), {'id': course_id}).fetchall()
            return jsonify([{ 'id': r[0], 'title': r[1], 'description': r[2], 'video_url': r[3], 'order_index': r[4], 'content': r[5] } for r in ls])
        except Exception:
            ls = db.session.execute(text(
                'SELECT LessonID, Title, Description, VideoUrl, OrderIndex FROM Lessons WHERE CourseID=:id ORDER BY OrderIndex, LessonID'
            ), {'id': course_id}).fetchall()
            return jsonify([{ 'id': r[0], 'title': r[1], 'description': r[2], 'video_url': r[3], 'order_index': r[4], 'content': None } for r in ls])
    # generic
    c = Course.query.get(course_id)
    if not c or (c.teacher_id and c.teacher_id != tid):
        return jsonify({'error': 'not found'}), 404
    ls = Lesson.query.filter_by(course_id=course_id).order_by(Lesson.order_index.asc().nullsfirst(), Lesson.id.asc()).all()
    return jsonify([{ 'id': l.id, 'title': l.title, 'description': l.description, 'video_url': l.video_url, 'order_index': l.order_index, 'content': l.content } for l in ls])


def create_lesson(course_id: int, data: dict):
    tid = int(get_jwt_identity())
    if db.get_engine().dialect.name == 'mssql':
        row = db.session.execute(text('SELECT TeacherID FROM Courses WHERE CourseID=:id'), {'id': course_id}).fetchone()
        if not row or (row[0] and int(row[0]) != tid):
            return jsonify({'error': 'not found'}), 404
        params = {'cid': course_id, 't': data.get('title') or 'Lesson', 'd': data.get('description'), 'v': data.get('video_url'), 'c': data.get('content')}
        try:
            r = db.session.execute(text(
                'INSERT INTO Lessons(CourseID, Title, Description, VideoUrl, Content) OUTPUT INSERTED.LessonID VALUES(:cid, :t, :d, :v, :c)'
            ), params).fetchone()
        except Exception:
            r = db.session.execute(text(
                'INSERT INTO Lessons(CourseID, Title, Description, VideoUrl) OUTPUT INSERTED.LessonID VALUES(:cid, :t, :d, :v)'
            ), params).fetchone()
        db.session.commit()
        return jsonify({'message': 'created', 'id': int(r[0])})
    c = Course.query.get(course_id)
    if not c or (c.teacher_id and c.teacher_id != tid):
        return jsonify({'error': 'not found'}), 404
    l = Lesson(course_id=course_id, title=data.get('title') or 'Lesson', description=data.get('description'), video_url=data.get('video_url'), content=data.get('content'))
    db.session.add(l)
    db.session.commit()
    return jsonify({'message': 'created', 'id': l.id})


def reorder_lessons(course_id: int, order: list[int]):
    # Order is an array of indices; apply by current id order
    if db.get_engine().dialect.name == 'mssql':
        ids = [r[0] for r in db.session.execute(text('SELECT LessonID FROM Lessons WHERE CourseID=:id ORDER BY LessonID'), {'id': course_id}).fetchall()]
        if not ids:
            return jsonify({'message': 'ok'})
        for idx, lid in enumerate(ids):
            new_idx = order[idx] if idx < len(order) else idx
            db.session.execute(text('UPDATE Lessons SET OrderIndex=:oi WHERE LessonID=:id'), {'oi': new_idx, 'id': lid})
        db.session.commit()
        return jsonify({'message': 'reordered'})
    ls = Lesson.query.filter_by(course_id=course_id).order_by(Lesson.id.asc()).all()
    if not ls:
        return jsonify({'message': 'ok'})
    for idx, l in enumerate(ls):
        l.order_index = order[idx] if idx < len(order) else idx
        db.session.add(l)
    db.session.commit()
    return jsonify({'message': 'reordered'})


def update_lesson(lesson_id: int, data: dict):
    if db.get_engine().dialect.name == 'mssql':
        # verify ownership via join
        row = db.session.execute(text(
            'SELECT c.TeacherID FROM [dbo].[Lessons] l JOIN [dbo].[Courses] c ON c.CourseID = l.CourseID WHERE l.LessonID = :id'
        ), {'id': lesson_id}).fetchone()
        tid = int(get_jwt_identity())
        if not row or (row[0] and int(row[0]) != tid):
            return jsonify({'error': 'not found'}), 404
        params = {'t': data.get('title'), 'd': data.get('description'), 'v': data.get('video_url'), 'c': data.get('content'), 'id': lesson_id}
        try:
            db.session.execute(text(
                'UPDATE [dbo].[Lessons] SET Title=:t, Description=:d, VideoUrl=:v, Content=:c WHERE LessonID=:id'
            ), params)
        except Exception:
            db.session.execute(text(
                'UPDATE [dbo].[Lessons] SET Title=:t, Description=:d, VideoUrl=:v WHERE LessonID=:id'
            ), params)
        db.session.commit()
        return jsonify({'message': 'updated'})
    # generic
    l = Lesson.query.get(lesson_id)
    if not l:
        return jsonify({'error': 'not found'}), 404
    tid = int(get_jwt_identity())
    c = Course.query.get(l.course_id)
    if not c or (c.teacher_id and c.teacher_id != tid):
        return jsonify({'error': 'not found'}), 404
    for k in ('title','description','video_url','order_index','content'):
        if k in data:
            setattr(l, k, data[k])
    db.session.add(l)
    db.session.commit()
    return jsonify({'message': 'updated'})


def delete_lesson(lesson_id: int):
    if db.get_engine().dialect.name == 'mssql':
        # verify ownership
        row = db.session.execute(text(
            'SELECT c.TeacherID FROM [dbo].[Lessons] l JOIN [dbo].[Courses] c ON c.CourseID = l.CourseID WHERE l.LessonID = :id'
        ), {'id': lesson_id}).fetchone()
        tid = int(get_jwt_identity())
        if not row or (row[0] and int(row[0]) != tid):
            return jsonify({'error': 'not found'}), 404
        db.session.execute(text('DELETE FROM [dbo].[Lessons] WHERE [LessonID]=:id'), {'id': lesson_id})
        db.session.commit()
        return jsonify({'message': 'deleted'})
    l = Lesson.query.get(lesson_id)
    if not l:
        return jsonify({'error': 'not found'}), 404
    tid = int(get_jwt_identity())
    c = Course.query.get(l.course_id)
    if not c or (c.teacher_id and c.teacher_id != tid):
        return jsonify({'error': 'not found'}), 404
    db.session.delete(l)
    db.session.commit()
    return jsonify({'message': 'deleted'})


def list_quiz_results(quiz_id: int):
    if db.get_engine().dialect.name == 'mssql':
        rows = db.session.execute(text(
            """
            SELECT r.[UserID], r.[Score], r.[SubmittedAt], u.[FullName]
            FROM [dbo].[QuizResults] r
            LEFT JOIN [dbo].[Users] u ON u.[UserID] = r.[UserID]
            WHERE r.[QuizID] = :qid
            ORDER BY r.[SubmittedAt] DESC
            """
        ), { 'qid': quiz_id }).fetchall()
        return jsonify([{ 'user_id': r[0], 'user_name': r[3], 'score': r[1], 'submitted_at': str(r[2]) } for r in rows])
    rows = db.session.execute(text(
        """
        SELECT r.user_id, r.score, r.submitted_at, u.fullname
        FROM quiz_results r
        LEFT JOIN users u ON u.id = r.user_id
        WHERE r.quiz_id = :qid
        ORDER BY r.submitted_at DESC
        """
    ), { 'qid': quiz_id }).fetchall()
    return jsonify([{ 'user_id': r[0], 'user_name': r[3], 'score': r[1], 'submitted_at': str(r[2]) } for r in rows])


def list_course_scores(course_id: int):
    """Return all quiz attempts for a teacher's course, including optional lesson mapping."""
    tid = int(get_jwt_identity())
    dialect = db.get_engine().dialect.name
    if dialect == 'mssql':
        course_row = db.session.execute(text(
            'SELECT [Title], [TeacherID] FROM [dbo].[Courses] WHERE [CourseID]=:cid'
        ), {'cid': course_id}).fetchone()
        if not course_row or (course_row[1] and int(course_row[1]) != tid):
            return jsonify({'error': 'not found'}), 404
        course_name = course_row[0]
        params = {'cid': course_id}
        sql = text("""
            SELECT r.[UserID], u.[FullName], r.[Score], r.[SubmittedAt],
                   q.[QuizID], q.[Title] AS QuizTitle,
                   q.[LessonID], l.[Title] AS LessonTitle
            FROM [dbo].[QuizResults] r
            JOIN [dbo].[Quizzes] q ON q.[QuizID] = r.[QuizID]
            LEFT JOIN [dbo].[Lessons] l ON q.[LessonID] = l.[LessonID]
            LEFT JOIN [dbo].[Users] u ON u.[UserID] = r.[UserID]
            WHERE q.[CourseID] = :cid
            ORDER BY r.[SubmittedAt] DESC
        """)
        try:
            rows = db.session.execute(sql, params).fetchall()
        except Exception:
            # Fallback for schemas without LessonID column
            fallback = text("""
                SELECT r.[UserID], u.[FullName], r.[Score], r.[SubmittedAt],
                       q.[QuizID], q.[Title] AS QuizTitle,
                       NULL AS LessonID, NULL AS LessonTitle
                FROM [dbo].[QuizResults] r
                JOIN [dbo].[Quizzes] q ON q.[QuizID] = r.[QuizID]
                LEFT JOIN [dbo].[Users] u ON u.[UserID] = r.[UserID]
                WHERE q.[CourseID] = :cid
                ORDER BY r.[SubmittedAt] DESC
            """)
            rows = db.session.execute(fallback, params).fetchall()
    else:
        course_row = db.session.execute(text(
            'SELECT name, teacher_id FROM courses WHERE id=:cid'
        ), {'cid': course_id}).fetchone()
        if not course_row or (course_row[1] and int(course_row[1]) != tid):
            return jsonify({'error': 'not found'}), 404
        course_name = course_row[0]
        params = {'cid': course_id}
        sql = text("""
            SELECT r.user_id, u.fullname, r.score, r.submitted_at,
                   q.id AS quiz_id, q.title AS quiz_title,
                   q.lesson_id, l.title AS lesson_title
            FROM quiz_results r
            JOIN quizzes q ON q.id = r.quiz_id
            LEFT JOIN lessons l ON q.lesson_id = l.id
            LEFT JOIN users u ON u.id = r.user_id
            WHERE q.course_id = :cid
            ORDER BY r.submitted_at DESC
        """)
        try:
            rows = db.session.execute(sql, params).fetchall()
        except Exception:
            fallback = text("""
                SELECT r.user_id, u.fullname, r.score, r.submitted_at,
                       q.id AS quiz_id, q.title AS quiz_title,
                       NULL AS lesson_id, NULL AS lesson_title
                FROM quiz_results r
                JOIN quizzes q ON q.id = r.quiz_id
                LEFT JOIN users u ON u.id = r.user_id
                WHERE q.course_id = :cid
                ORDER BY r.submitted_at DESC
            """)
            rows = db.session.execute(fallback, params).fetchall()

    items = [{
        'user_id': row[0],
        'user_name': row[1] or '',
        'score': float(row[2] or 0),
        'submitted_at': str(row[3]) if row[3] else '',
        'quiz_id': row[4],
        'quiz_title': row[5] or '',
        'lesson_id': row[6],
        'lesson_title': row[7]
    } for row in rows]
    student_ids = {item['user_id'] for item in items if item['user_id'] is not None}
    quiz_ids = {item['quiz_id'] for item in items if item['quiz_id'] is not None}
    avg_score = round(sum(item['score'] for item in items) / len(items), 2) if items else 0.0
    return jsonify({
        'course_id': course_id,
        'course_name': course_name,
        'results': items,
        'summary': {
            'students': len(student_ids),
            'quizzes': len(quiz_ids),
            'attempts': len(items),
            'average_score': avg_score
        }
    })


def create_question(quiz_id: int, data: dict):
    # Use raw insert with proper table/columns per dialect
    if db.get_engine().dialect.name == 'mssql':
        db.session.execute(text(
            """
            INSERT INTO [dbo].[QuizQuestions]
            ([QuizID], [QuestionText], [OptionA], [OptionB], [OptionC], [OptionD], [CorrectOption])
            VALUES(:qid, :qt, :a, :b, :c, :d, :co)
            """
        ), {
            'qid': quiz_id,
            'qt': data.get('question_text',''),
            'a': data.get('option_a'),
            'b': data.get('option_b'),
            'c': data.get('option_c'),
            'd': data.get('option_d'),
            'co': (data.get('correct_option') or 'A')[:1]
        })
        db.session.commit()
        return jsonify({'message': 'added'})
    db.session.execute(text(
        """
        INSERT INTO quiz_questions(quiz_id, question_text, option_a, option_b, option_c, option_d, correct_option)
        VALUES(:qid, :qt, :a, :b, :c, :d, :co)
        """
    ), { 'qid': quiz_id, 'qt': data.get('question_text',''), 'a': data.get('option_a'), 'b': data.get('option_b'), 'c': data.get('option_c'), 'd': data.get('option_d'), 'co': data.get('correct_option') })
    db.session.commit()
    return jsonify({'message': 'added'})


def update_quiz(quiz_id: int, data: dict):
    if db.get_engine().dialect.name == 'mssql':
        # verify ownership via quiz -> course
        row = db.session.execute(text(
            'SELECT q.CourseID, q.LessonID, c.TeacherID FROM [dbo].[Quizzes] q JOIN [dbo].[Courses] c ON c.CourseID=q.CourseID WHERE q.QuizID=:id'
        ), {'id': quiz_id}).fetchone()
        tid = int(get_jwt_identity())
        if not row or (row[2] and int(row[2]) != tid):
            return jsonify({'error':'not found'}), 404
        lesson_id = data.get('lesson_id', row[1])
        if lesson_id:
            lesson = db.session.execute(text(
                'SELECT LessonID FROM [dbo].[Lessons] WHERE LessonID=:lid AND CourseID=:cid'
            ), {'lid': lesson_id, 'cid': row[0]}).fetchone()
            if not lesson:
                return jsonify({'error':'lesson not found in course'}), 400
        db.session.execute(text(
            'UPDATE [dbo].[Quizzes] SET Title=:t, Description=:d, TimeLimit=:tl, LessonID=:lid WHERE QuizID=:id'
        ), {'t': data.get('title'), 'd': data.get('description'), 'tl': data.get('time_limit'), 'lid': lesson_id, 'id': quiz_id})
        db.session.commit()
        return jsonify({'message':'updated'})
    # generic
    q = db.session.execute(text('SELECT id, course_id, lesson_id FROM quizzes WHERE id=:id'), {'id': quiz_id}).fetchone()
    if not q:
        return jsonify({'error':'not found'}), 404
    c = db.session.execute(text('SELECT id, teacher_id FROM courses WHERE id=:id'), {'id': q[1]}).fetchone()
    tid = int(get_jwt_identity())
    if not c or (c[1] and int(c[1]) != tid):
        return jsonify({'error':'not found'}), 404
    lesson_id = data.get('lesson_id', q[2])
    if lesson_id:
        lesson = Lesson.query.filter_by(id=lesson_id, course_id=q[1]).first()
        if not lesson:
            return jsonify({'error': 'lesson not found in course'}), 400
    db.session.execute(text('UPDATE quizzes SET title=:t, description=:d, time_limit=:tl, lesson_id=:lid WHERE id=:id'),
                       {'t': data.get('title'), 'd': data.get('description'), 'tl': data.get('time_limit'), 'lid': lesson_id, 'id': quiz_id})
    db.session.commit()
    return jsonify({'message':'updated'})


def delete_quiz(quiz_id: int):
    if db.get_engine().dialect.name == 'mssql':
        row = db.session.execute(text(
            'SELECT c.TeacherID FROM [dbo].[Quizzes] q JOIN [dbo].[Courses] c ON c.CourseID=q.CourseID WHERE q.QuizID=:id'
        ), {'id': quiz_id}).fetchone()
        tid = int(get_jwt_identity())
        if not row or (row[0] and int(row[0]) != tid):
            return jsonify({'error':'not found'}), 404
        db.session.execute(text('DELETE FROM [dbo].[QuizQuestions] WHERE [QuizID]=:id'), {'id': quiz_id})
        db.session.execute(text('DELETE FROM [dbo].[Quizzes] WHERE [QuizID]=:id'), {'id': quiz_id})
        db.session.commit()
        return jsonify({'message':'deleted'})
    # generic
    q = db.session.execute(text('SELECT id, course_id FROM quizzes WHERE id=:id'), {'id': quiz_id}).fetchone()
    if not q:
        return jsonify({'error':'not found'}), 404
    c = db.session.execute(text('SELECT id, teacher_id FROM courses WHERE id=:id'), {'id': q[1]}).fetchone()
    tid = int(get_jwt_identity())
    if not c or (c[1] and int(c[1]) != tid):
        return jsonify({'error':'not found'}), 404
    db.session.execute(text('DELETE FROM quiz_questions WHERE quiz_id=:id'), {'id': quiz_id})
    db.session.execute(text('DELETE FROM quizzes WHERE id=:id'), {'id': quiz_id})
    db.session.commit()
    return jsonify({'message':'deleted'})


def update_question(question_id: int, data: dict):
    if db.get_engine().dialect.name == 'mssql':
        # verify ownership via question -> quiz -> course
        row = db.session.execute(text(
            'SELECT c.TeacherID FROM [dbo].[QuizQuestions] qq JOIN [dbo].[Quizzes] q ON q.QuizID=qq.QuizID JOIN [dbo].[Courses] c ON c.CourseID=q.CourseID WHERE qq.QuestionID=:id'
        ), {'id': question_id}).fetchone()
        tid = int(get_jwt_identity())
        if not row or (row[0] and int(row[0]) != tid):
            return jsonify({'error':'not found'}), 404
        db.session.execute(text(
            'UPDATE [dbo].[QuizQuestions] SET QuestionText=:qt, OptionA=:a, OptionB=:b, OptionC=:c, OptionD=:d, CorrectOption=:co WHERE QuestionID=:id'
        ), {'qt': data.get('question_text'), 'a': data.get('option_a'), 'b': data.get('option_b'), 'c': data.get('option_c'), 'd': data.get('option_d'), 'co': (data.get('correct_option') or 'A')[:1], 'id': question_id})
        db.session.commit()
        return jsonify({'message':'updated'})
    # generic
    db.session.execute(text(
        'UPDATE quiz_questions SET question_text=:qt, option_a=:a, option_b=:b, option_c=:c, option_d=:d, correct_option=:co WHERE id=:id'
    ), {'qt': data.get('question_text'), 'a': data.get('option_a'), 'b': data.get('option_b'), 'c': data.get('option_c'), 'd': data.get('option_d'), 'co': (data.get('correct_option') or 'A')[:1], 'id': question_id})
    db.session.commit()
    return jsonify({'message':'updated'})


def delete_question(question_id: int):
    if db.get_engine().dialect.name == 'mssql':
        row = db.session.execute(text(
            'SELECT c.TeacherID FROM [dbo].[QuizQuestions] qq JOIN [dbo].[Quizzes] q ON q.QuizID=qq.QuizID JOIN [dbo].[Courses] c ON c.CourseID=q.CourseID WHERE qq.QuestionID=:id'
        ), {'id': question_id}).fetchone()
        tid = int(get_jwt_identity())
        if not row or (row[0] and int(row[0]) != tid):
            return jsonify({'error':'not found'}), 404
        db.session.execute(text('DELETE FROM [dbo].[QuizQuestions] WHERE [QuestionID]=:id'), {'id': question_id})
        db.session.commit()
        return jsonify({'message':'deleted'})
    db.session.execute(text('DELETE FROM quiz_questions WHERE id=:id'), {'id': question_id})
    db.session.commit()
    return jsonify({'message':'deleted'})


def list_quizzes(course_id: int):
    if db.get_engine().dialect.name == 'mssql':
        rows = db.session.execute(text(
            'SELECT QuizID, Title, Description, TotalQuestions, TimeLimit, CreatedAt FROM [dbo].[Quizzes] WHERE CourseID=:cid ORDER BY QuizID DESC'
        ), {'cid': course_id}).fetchall()
        return jsonify([{ 'id': r[0], 'title': r[1], 'description': r[2], 'total_questions': r[3], 'time_limit': r[4], 'created_at': str(r[5]) if r[5] else '' } for r in rows])
    qs = Quiz.query.filter_by(course_id=course_id).order_by(Quiz.id.desc()).all()
    return jsonify([{ 'id': q.id, 'title': q.title, 'description': q.description, 'total_questions': q.total_questions, 'time_limit': q.time_limit, 'created_at': str(q.created_at) if q.created_at else '' } for q in qs])


def create_quiz(course_id: int, data: dict):
    tid = int(get_jwt_identity())
    lesson_id = data.get('lesson_id')
    if not lesson_id:
        return jsonify({'error': 'lesson_id is required'}), 400
    if db.get_engine().dialect.name == 'mssql':
        owner = db.session.execute(text('SELECT TeacherID FROM [dbo].[Courses] WHERE CourseID=:id'), {'id': course_id}).fetchone()
        if not owner or (owner[0] and int(owner[0]) != tid):
            return jsonify({'error': 'not found'}), 404
        lesson = db.session.execute(text(
            'SELECT LessonID FROM [dbo].[Lessons] WHERE LessonID=:lid AND CourseID=:cid'
        ), {'lid': lesson_id, 'cid': course_id}).fetchone()
        if not lesson:
            return jsonify({'error': 'lesson not found in course'}), 400
        row = db.session.execute(text(
            'INSERT INTO [dbo].[Quizzes](CourseID, LessonID, Title, Description, TotalQuestions, TimeLimit, CreatedAt) OUTPUT INSERTED.QuizID VALUES(:cid,:lid,:t,:d,0,:tl,GETDATE())'
        ), {'cid': course_id, 'lid': lesson_id, 't': data.get('title') or 'New Quiz', 'd': data.get('description'), 'tl': data.get('time_limit') or 0}).fetchone()
        db.session.commit()
        return jsonify({'message': 'created', 'id': int(row[0])}), 201
    # generic ORM
    lesson = Lesson.query.filter_by(id=lesson_id, course_id=course_id).first()
    if not lesson:
        return jsonify({'error': 'lesson not found in course'}), 400
    q = Quiz(course_id=course_id, lesson_id=lesson_id, title=data.get('title') or 'New Quiz', description=data.get('description'), total_questions=0, time_limit=data.get('time_limit'))
    db.session.add(q)
    db.session.commit()
    return jsonify({'message': 'created', 'id': q.id}), 201


def list_subscribers(course_id: int):
    if db.get_engine().dialect.name == 'mssql':
        rows = db.session.execute(text(
            """
            SELECT e.[EnrollmentID], e.[UserID], e.[Status], u.[FullName] AS fullname, u.[Email] AS email
            FROM [dbo].[Enrollments] e
            LEFT JOIN [dbo].[Users] u ON u.[UserID] = e.[UserID]
            WHERE e.[CourseID] = :cid
            ORDER BY e.[EnrollmentID] DESC
            """
        ), { 'cid': course_id }).fetchall()
        return jsonify([{ 'id': r[0], 'user_id': r[1], 'fullname': r[3], 'email': r[4], 'status': r[2] } for r in rows])
    rows = db.session.execute(text(
        """
        SELECT e.id, e.student_id, e.status, u.fullname AS fullname, u.email AS email
        FROM enrollments e
        LEFT JOIN users u ON u.id = e.student_id
        WHERE e.course_id = :cid
        ORDER BY e.id DESC
        """
    ), { 'cid': course_id }).fetchall()
    return jsonify([{ 'id': r[0], 'user_id': r[1], 'fullname': r[3], 'email': r[4], 'status': r[2] } for r in rows])


def approve_subscriber(enroll_id: int):
    if db.get_engine().dialect.name == 'mssql':
        r = db.session.execute(text('UPDATE [dbo].[Enrollments] SET [Status]=:st WHERE [EnrollmentID]=:id'), {'st': 'approved', 'id': enroll_id})
        if r.rowcount == 0:
            return jsonify({'error':'not found'}), 404
        db.session.commit()
        return jsonify({'message':'approved'})
    e = Enrollment.query.get(enroll_id)
    if not e:
        return jsonify({'error':'not found'}), 404
    e.status = 'approved'
    db.session.add(e)
    db.session.commit()
    return jsonify({'message':'approved'})


def remove_subscriber(enroll_id: int):
    if db.get_engine().dialect.name == 'mssql':
        r = db.session.execute(text('DELETE FROM [dbo].[Enrollments] WHERE [EnrollmentID]=:id'), {'id': enroll_id})
        if r.rowcount == 0:
            return jsonify({'error':'not found'}), 404
        db.session.commit()
        return jsonify({'message':'removed'})
    e = Enrollment.query.get(enroll_id)
    if not e:
        return jsonify({'error':'not found'}), 404
    db.session.delete(e)
    db.session.commit()
    return jsonify({'message':'removed'})
