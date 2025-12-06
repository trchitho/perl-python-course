from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import func, distinct, text
from app import db
from app.models.course_model import Course
from app.models.lesson_model import Lesson
from app.models.quiz_model import Quiz, QuizQuestion, QuizResult
from app.models.enrollment_model import Enrollment

def list_quizzes_for_course(course_id: int):
    """Lists all quizzes for a given course, including lesson details."""
    quizzes = Quiz.query.filter_by(course_id=course_id).options(
        db.joinedload(Quiz.lesson)
    ).order_by(Quiz.id.desc()).all()

    return jsonify([{
        'id': q.id,
        'title': q.title,
        'description': q.description,
        'total_questions': q.total_questions,
        'time_limit': q.time_limit,
        'created_at': q.created_at.isoformat() if q.created_at else '',
        'lesson_id': q.lesson_id,
        'lesson_title': q.lesson.title if q.lesson else ''
    } for q in quizzes])

def get_quiz_detail(quiz_id: int):
    """
    Gets the details and questions for a quiz, without revealing correct answers.
    """
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify({'error': 'Quiz not found'}), 404
    
    questions = QuizQuestion.query.filter_by(quiz_id=quiz_id).order_by(QuizQuestion.id).all()
    
    return jsonify({
        'id': quiz.id,
        'title': quiz.title,
        'description': quiz.description,
        'total_questions': quiz.total_questions,
        'time_limit': quiz.time_limit,
        'course_id': quiz.course_id,
        'lesson_id': quiz.lesson_id,
        'questions': [{
            'id': q.id,
            'question_text': q.question_text,
            'option_a': q.option_a or '',
            'option_b': q.option_b or '',
            'option_c': q.option_c or '',
            'option_d': q.option_d or ''
        } for q in questions]
    })

def submit_quiz(quiz_id: int, answers: dict):
    """
    Submits a student's answers for a quiz, calculates the score, and saves the result.
    """
    user_id = int(get_jwt_identity())
    if not isinstance(answers, dict):
        return jsonify({'message': 'Invalid answers format'}), 400

    questions = QuizQuestion.query.filter_by(quiz_id=quiz_id).all()
    total = len(questions)
    correct = 0

    for q in questions:
        # User's answer for the current question
        user_answer = (answers.get(str(q.id)) or '').strip().upper()
        if user_answer and q.correct_option and user_answer == q.correct_option.strip().upper():
            correct += 1

    score = round((correct / total) * 100.0, 2) if total > 0 else 0.0

    # Store result
    try:
        new_result = QuizResult(quiz_id=quiz_id, user_id=user_id, score=score)
        db.session.add(new_result)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        # Still return the score to the user even if db write fails
        return jsonify({
            'message': f'Failed to record result: {e}',
            'score': score, 'correct': correct, 'total': total
        }), 200

    return jsonify({'message': 'Quiz submitted successfully', 'score': score, 'correct': correct, 'total': total})

def list_quiz_results_for_student():
    """Lists all quiz results for the current student."""
    from sqlalchemy import text
    user_id = int(get_jwt_identity())
    
    # Try ORM first, fallback to raw SQL for MSSQL
    if db.get_engine().dialect.name == 'mssql':
        try:
            # Try with QuizResults (PascalCase)
            rows = db.session.execute(text(
                'SELECT qr.[ResultID], qr.[QuizID], qr.[UserID], qr.[Score], qr.[SubmittedAt], '
                'q.[Title] as QuizTitle, c.[Title] as CourseName, l.[Title] as LessonTitle '
                'FROM [dbo].[QuizResults] qr '
                'LEFT JOIN [dbo].[Quizzes] q ON q.[QuizID] = qr.[QuizID] '
                'LEFT JOIN [dbo].[Courses] c ON c.[CourseID] = q.[CourseID] '
                'LEFT JOIN [dbo].[Lessons] l ON l.[LessonID] = q.[LessonID] '
                'WHERE qr.[UserID] = :uid ORDER BY qr.[SubmittedAt] DESC'
            ), {'uid': user_id}).fetchall()
            
            return jsonify([{
                'id': row[0],
                'quiz_id': row[1],
                'score': float(row[3]) if row[3] else 0.0,
                'submitted_at': row[4].isoformat() if row[4] else '',
                'quiz_title': row[5] or 'N/A',
                'course_title': row[6] or 'N/A',
                'lesson_title': row[7] or ''
            } for row in rows])
        except Exception as e:
            # Fallback: return empty list if table doesn't exist
            print(f"[Warning] QuizResults table not found or error: {e}")
            return jsonify([])
    
    # Generic ORM path
    try:
        results = QuizResult.query.filter_by(user_id=user_id).options(
            db.joinedload(QuizResult.quiz).joinedload(Quiz.lesson),
            db.joinedload(QuizResult.quiz).joinedload(Quiz.course)
        ).order_by(QuizResult.submitted_at.desc()).all()

        return jsonify([{
            'id': r.id,
            'quiz_id': r.quiz_id,
            'score': r.score,
            'submitted_at': r.submitted_at.isoformat() if r.submitted_at else '',
            'quiz_title': r.quiz.title if r.quiz else 'N/A',
            'lesson_title': r.quiz.lesson.title if r.quiz and r.quiz.lesson else '',
            'course_title': r.quiz.course.name if r.quiz and r.quiz.course else 'N/A'
        } for r in results])
    except Exception as e:
        print(f"[Warning] Error querying quiz results: {e}")
        return jsonify([])

def list_quizzes_for_lesson(lesson_id: int):
    """Lists all quizzes for a specific lesson."""
    quizzes = Quiz.query.filter_by(lesson_id=lesson_id).order_by(Quiz.id).all()
    
    return jsonify([{
        'id': q.id,
        'title': q.title,
        'description': q.description,
        'total_questions': q.total_questions,
        'time_limit': q.time_limit,
        'created_at': q.created_at.isoformat() if q.created_at else ''
    } for q in quizzes])

def list_progress_for_student():
    """
    Calculates and lists the progress for each course the student is enrolled in.
    """
    user_id = int(get_jwt_identity())

    enrolled_courses = Course.query.join(Enrollment).filter(Enrollment.student_id == user_id).all()
    
    result = []
    for course in enrolled_courses:
        cid = course.id
        
        total_lessons = Lesson.query.filter_by(course_id=cid).count()
        total_quizzes = Quiz.query.filter_by(course_id=cid).count()

        # Subquery to get quiz results for the current user and course
        results_subquery = db.session.query(QuizResult.quiz_id, QuizResult.score) \
            .join(Quiz, Quiz.id == QuizResult.quiz_id) \
            .filter(QuizResult.user_id == user_id, Quiz.course_id == cid).subquery()

        # Completed quizzes
        completed_quizzes_count = db.session.query(func.count(distinct(results_subquery.c.quiz_id))).scalar()
        
        # Average score
        avg_score = db.session.query(func.avg(results_subquery.c.score)).scalar() or 0.0

        # Completed lessons (lessons with at least one completed quiz)
        completed_lessons_count = db.session.query(func.count(distinct(Quiz.lesson_id))) \
            .join(results_subquery, Quiz.id == results_subquery.c.quiz_id) \
            .filter(Quiz.lesson_id.isnot(None)).scalar()
        
        # Calculate progress percentage
        progress_percent = 0
        if total_lessons > 0:
            progress_percent = int((completed_lessons_count / total_lessons) * 100)
        elif total_quizzes > 0:
            progress_percent = int((completed_quizzes_count / total_quizzes) * 100)

        result.append({
            'course_id': cid,
            'course_title': course.name,
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons_count,
            'total_quizzes': total_quizzes,
            'completed_quizzes': completed_quizzes_count,
            'progress_percent': progress_percent,
            'avg_score': round(float(avg_score), 2)
        })
        
    return jsonify(result)
