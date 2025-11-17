from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import text
from app import db


def list_quizzes_for_course(course_id: int):
    if db.get_engine().dialect.name == 'mssql':
        try:
            rows = db.session.execute(text(
                '''
                SELECT q.[QuizID], q.[Title], q.[Description], q.[TotalQuestions], q.[TimeLimit], q.[CreatedAt],
                       q.[LessonID], l.[Title] AS LessonTitle
                FROM [dbo].[Quizzes] q
                LEFT JOIN [dbo].[Lessons] l ON l.[LessonID] = q.[LessonID]
                WHERE q.[CourseID]=:cid
                ORDER BY q.[QuizID] DESC
                '''
            ), {'cid': course_id}).fetchall()
        except Exception:
            rows = db.session.execute(text(
                '''
                SELECT q.[QuizID], q.[Title], q.[Description], q.[TotalQuestions], q.[TimeLimit], q.[CreatedAt]
                FROM [dbo].[Quizzes] q
                WHERE q.[CourseID]=:cid
                ORDER BY q.[QuizID] DESC
                '''
            ), {'cid': course_id}).fetchall()
            return jsonify([{
                'id': r[0], 'title': r[1], 'description': r[2], 'total_questions': r[3],
                'time_limit': r[4], 'created_at': str(r[5]) if r[5] else '',
                'lesson_id': None, 'lesson_title': ''
            } for r in rows])
        return jsonify([{
            'id': r[0], 'title': r[1], 'description': r[2], 'total_questions': r[3],
            'time_limit': r[4], 'created_at': str(r[5]) if r[5] else '',
            'lesson_id': r[6], 'lesson_title': r[7] or ''
        } for r in rows])
    rows = db.session.execute(text(
        '''
        SELECT q.id, q.title, q.description, q.total_questions, q.time_limit, q.created_at,
               q.lesson_id, l.title AS lesson_title
        FROM quizzes q
        LEFT JOIN lessons l ON l.id = q.lesson_id
        WHERE q.course_id=:cid
        ORDER BY q.id DESC
        '''
    ), {'cid': course_id}).fetchall()
    return jsonify([{
        'id': r[0], 'title': r[1], 'description': r[2], 'total_questions': r[3],
        'time_limit': r[4], 'created_at': str(r[5]) if r[5] else '',
        'lesson_id': r[6], 'lesson_title': r[7] or ''
    } for r in rows])


def get_quiz_detail(quiz_id: int):
    # Return questions without revealing correct answers
    if db.get_engine().dialect.name == 'mssql':
        rows = db.session.execute(text(
            'SELECT [QuestionID], [QuestionText], [OptionA], [OptionB], [OptionC], [OptionD] '
            'FROM [dbo].[QuizQuestions] WHERE [QuizID]=:qid ORDER BY [QuestionID]'
        ), {'qid': quiz_id}).fetchall()
    else:
        rows = db.session.execute(text(
            'SELECT id, question_text, option_a, option_b, option_c, option_d FROM quiz_questions WHERE quiz_id=:qid ORDER BY id'
        ), {'qid': quiz_id}).fetchall()
    return jsonify([{
        'id': r[0], 'question_text': r[1], 'option_a': r[2] or '', 'option_b': r[3] or '', 'option_c': r[4] or '', 'option_d': r[5] or ''
    } for r in rows])


def submit_quiz(quiz_id: int, answers: dict):
    """answers is a dict: { question_id: 'A'|'B'|'C'|'D' }"""
    user_id = int(get_jwt_identity())
    if not isinstance(answers, dict):
        return jsonify({'message': 'Invalid answers'}), 400

    if db.get_engine().dialect.name == 'mssql':
        rows = db.session.execute(text(
            'SELECT [QuestionID], [CorrectOption] FROM [dbo].[QuizQuestions] WHERE [QuizID]=:qid'
        ), {'qid': quiz_id}).fetchall()
    else:
        rows = db.session.execute(text(
            'SELECT id, correct_option FROM quiz_questions WHERE quiz_id=:qid'
        ), {'qid': quiz_id}).fetchall()

    total = len(rows) or 0
    correct = 0
    for qid, correct_opt in rows:
        chosen = (answers.get(str(qid)) or answers.get(int(qid)) or '').strip().upper()[:1]
        if chosen and correct_opt and chosen == str(correct_opt).upper()[:1]:
            correct += 1

    score = round((correct / total) * 100.0, 2) if total else 0.0

    # Store result
    try:
        if db.get_engine().dialect.name == 'mssql':
            db.session.execute(text(
                'INSERT INTO [dbo].[QuizResults] ([QuizID],[UserID],[Score],[SubmittedAt]) VALUES(:qid,:uid,:s,GETDATE())'
            ), {'qid': quiz_id, 'uid': user_id, 's': score})
        else:
            db.session.execute(text(
                'INSERT INTO quiz_results (quiz_id,user_id,score,submitted_at) VALUES(:qid,:uid,:s, CURRENT_TIMESTAMP)'
            ), {'qid': quiz_id, 'uid': user_id, 's': score})
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({'message': 'Failed to record result', 'score': score, 'correct': correct, 'total': total}), 200

    return jsonify({'message': 'submitted', 'score': score, 'correct': correct, 'total': total})


def list_quiz_results_for_student():
    uid = int(get_jwt_identity())
    if db.get_engine().dialect.name == 'mssql':
        try:
            rows = db.session.execute(text(
                """
                SELECT r.[ResultID], r.[QuizID], r.[Score], r.[SubmittedAt],
                       q.[Title] AS QuizTitle, l.[Title] AS LessonTitle, c.[Title] AS CourseTitle
                FROM [dbo].[QuizResults] r
                JOIN [dbo].[Quizzes] q ON q.[QuizID] = r.[QuizID]
                LEFT JOIN [dbo].[Lessons] l ON l.[LessonID] = q.[LessonID]
                LEFT JOIN [dbo].[Courses] c ON c.[CourseID] = q.[CourseID]
                WHERE r.[UserID] = :uid
                ORDER BY r.[SubmittedAt] DESC
                """
            ), {'uid': uid}).fetchall()
        except Exception:
            rows = db.session.execute(text(
                """
                SELECT r.[ResultID], r.[QuizID], r.[Score], r.[SubmittedAt],
                       q.[Title] AS QuizTitle, c.[Title] AS CourseTitle
                FROM [dbo].[QuizResults] r
                JOIN [dbo].[Quizzes] q ON q.[QuizID] = r.[QuizID]
                LEFT JOIN [dbo].[Courses] c ON c.[CourseID] = q.[CourseID]
                WHERE r.[UserID] = :uid
                ORDER BY r.[SubmittedAt] DESC
                """
            ), {'uid': uid}).fetchall()
            return jsonify([
                {
                    'id': r[0],
                    'quiz_id': r[1],
                    'score': r[2],
                    'submitted_at': str(r[3]) if r[3] else '',
                    'quiz_title': r[4],
                    'lesson_title': '',
                    'course_title': r[5]
                } for r in rows
            ])
    else:
        rows = db.session.execute(text(
            """
            SELECT r.id, r.quiz_id, r.score, r.submitted_at,
                   q.title, l.title AS lesson_title, c.name AS course_name
            FROM quiz_results r
            JOIN quizzes q ON q.id = r.quiz_id
            LEFT JOIN lessons l ON l.id = q.lesson_id
            LEFT JOIN courses c ON c.id = q.course_id
            WHERE r.user_id = :uid
            ORDER BY r.submitted_at DESC
            """
        ), {'uid': uid}).fetchall()
    return jsonify([
        {
            'id': r[0],
            'quiz_id': r[1],
            'score': r[2],
            'submitted_at': str(r[3]) if r[3] else '',
            'quiz_title': r[4],
            'lesson_title': r[5],
            'course_title': r[6]
        } for r in rows
    ])


def list_progress_for_student():
    uid = int(get_jwt_identity())
    dialect = db.get_engine().dialect.name
    if dialect == 'mssql':
        courses = db.session.execute(text(
            """
            SELECT c.[CourseID], c.[Title]
            FROM [dbo].[Enrollments] e
            JOIN [dbo].[Courses] c ON c.[CourseID] = e.[CourseID]
            WHERE e.[UserID] = :uid
            """
        ), {'uid': uid}).fetchall()
        result = []
        for cid, title in courses:
            total_lessons = db.session.execute(text(
                'SELECT COUNT(*) FROM [dbo].[Lessons] WHERE [CourseID]=:cid'
            ), {'cid': cid}).scalar() or 0
            completed_lessons = db.session.execute(text(
                """
                SELECT COUNT(DISTINCT q.[LessonID]) FROM [dbo].[QuizResults] r
                JOIN [dbo].[Quizzes] q ON q.[QuizID]=r.[QuizID]
                WHERE r.[UserID]=:uid AND q.[CourseID]=:cid AND q.[LessonID] IS NOT NULL
                """
            ), {'uid': uid, 'cid': cid}).scalar() or 0
            avg_score_row = db.session.execute(text(
                """
                SELECT AVG(r.[Score]) FROM [dbo].[QuizResults] r
                JOIN [dbo].[Quizzes] q ON q.[QuizID]=r.[QuizID]
                WHERE r.[UserID]=:uid AND q.[CourseID]=:cid
                """
            ), {'uid': uid, 'cid': cid}).fetchone()
            avg_score = float(avg_score_row[0]) if avg_score_row and avg_score_row[0] is not None else 0.0
            total_quizzes = db.session.execute(text(
                'SELECT COUNT(*) FROM [dbo].[Quizzes] WHERE [CourseID]=:cid'
            ), {'cid': cid}).scalar() or 0
            completed_quizzes = db.session.execute(text(
                """
                SELECT COUNT(DISTINCT r.[QuizID]) FROM [dbo].[QuizResults] r
                JOIN [dbo].[Quizzes] q ON q.[QuizID]=r.[QuizID]
                WHERE r.[UserID]=:uid AND q.[CourseID]=:cid
                """
            ), {'uid': uid, 'cid': cid}).scalar() or 0
            percent = int((completed_lessons / total_lessons) * 100) if total_lessons else int((completed_quizzes/total_quizzes)*100) if total_quizzes else 0
            result.append({
                'course_id': cid,
                'course_title': title,
                'total_lessons': int(total_lessons),
                'completed_lessons': int(completed_lessons),
                'total_quizzes': int(total_quizzes),
                'completed_quizzes': int(completed_quizzes),
                'progress_percent': percent,
                'avg_score': round(avg_score, 2)
            })
        return jsonify(result)
    # generic SQL
    courses = db.session.execute(text(
        """
        SELECT c.id, c.name
        FROM enrollments e
        JOIN courses c ON c.id = e.course_id
        WHERE e.student_id = :uid
        """
    ), {'uid': uid}).fetchall()
    result = []
    for cid, title in courses:
        total_lessons = db.session.execute(text(
            'SELECT COUNT(*) FROM lessons WHERE course_id=:cid'
        ), {'cid': cid}).scalar() or 0
        completed_lessons = db.session.execute(text(
            """
            SELECT COUNT(DISTINCT q.lesson_id)
            FROM quiz_results r
            JOIN quizzes q ON q.id = r.quiz_id
            WHERE r.user_id=:uid AND q.course_id=:cid AND q.lesson_id IS NOT NULL
            """
        ), {'uid': uid, 'cid': cid}).scalar() or 0
        avg_score_row = db.session.execute(text(
            """
            SELECT AVG(r.score) FROM quiz_results r
            JOIN quizzes q ON q.id = r.quiz_id
            WHERE r.user_id=:uid AND q.course_id=:cid
            """
        ), {'uid': uid, 'cid': cid}).fetchone()
        avg_score = float(avg_score_row[0]) if avg_score_row and avg_score_row[0] is not None else 0.0
        total_quizzes = db.session.execute(text(
            'SELECT COUNT(*) FROM quizzes WHERE course_id=:cid'
        ), {'cid': cid}).scalar() or 0
        completed_quizzes = db.session.execute(text(
            """
            SELECT COUNT(DISTINCT r.quiz_id)
            FROM quiz_results r
            JOIN quizzes q ON q.id = r.quiz_id
            WHERE r.user_id=:uid AND q.course_id=:cid
            """
        ), {'uid': uid, 'cid': cid}).scalar() or 0
        percent = int((completed_lessons / total_lessons) * 100) if total_lessons else int((completed_quizzes/total_quizzes)*100) if total_quizzes else 0
        result.append({
            'course_id': cid,
            'course_title': title,
            'total_lessons': int(total_lessons),
            'completed_lessons': int(completed_lessons),
            'total_quizzes': int(total_quizzes),
            'completed_quizzes': int(completed_quizzes),
            'progress_percent': percent,
            'avg_score': round(avg_score, 2)
        })
    return jsonify(result)
