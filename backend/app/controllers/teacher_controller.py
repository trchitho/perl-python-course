from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import func
import os
from app import db
from app.models.user_model import User
from app.models.course_model import Course
from app.models.lesson_model import Lesson
from app.models.quiz_model import Quiz, QuizQuestion, QuizResult
from app.models.enrollment_model import Enrollment
from app.services.quiz_import_service import parse_quiz_from_docx

# --- Helper Functions ---

def _get_teacher_course(course_id: int, teacher_id: int):
    """
    Fetches a course and verifies that it belongs to the specified teacher.
    Returns the course object or (None, error_response).
    """
    course = Course.query.get(course_id)
    if not course:
        return None, (jsonify({'error': 'Course not found'}), 404)
    if course.teacher_id != teacher_id:
        return None, (jsonify({'error': 'You do not have permission for this course'}), 403)
    return course, None

def _get_teacher_quiz(quiz_id: int, teacher_id: int):
    """
    Fetches a quiz and verifies that it belongs to the specified teacher.
    """
    quiz = Quiz.query.options(db.joinedload(Quiz.course)).get(quiz_id)
    if not quiz:
        return None, (jsonify({'error': 'Quiz not found'}), 404)
    if quiz.course.teacher_id != teacher_id:
        return None, (jsonify({'error': 'You do not have permission for this quiz'}), 403)
    return quiz, None

def _get_teacher_lesson(lesson_id: int, teacher_id: int):
    """
    Fetches a lesson and verifies that it belongs to the specified teacher.
    """
    lesson = Lesson.query.options(db.joinedload(Lesson.course)).get(lesson_id)
    if not lesson:
        return None, (jsonify({'error': 'Lesson not found'}), 404)
    if lesson.course.teacher_id != teacher_id:
        return None, (jsonify({'error': 'You do not have permission for this lesson'}), 403)
    return lesson, None
    
# --- Controller Functions ---

def stats_for_teacher():
    tid = int(get_jwt_identity())
    
    courses_count = Course.query.filter_by(teacher_id=tid).count()
    
    student_count = db.session.query(func.count(Enrollment.student_id.distinct())).\
        join(Course).\
        filter(Course.teacher_id == tid).scalar() or 0

    lessons_count = db.session.query(func.count(Lesson.id)).\
        join(Course).\
        filter(Course.teacher_id == tid).scalar() or 0

    quiz_count = db.session.query(func.count(Quiz.id)).\
        join(Course).\
        filter(Course.teacher_id == tid).scalar() or 0

    avg_score = db.session.query(func.avg(QuizResult.score)).\
        join(Quiz).join(Course).\
        filter(Course.teacher_id == tid).scalar() or 0.0

    return jsonify({
        'courses': courses_count,
        'students': student_count or 0,
        'lessons': lessons_count,
        'quizzes': quiz_count,
        'avg_score': round(float(avg_score), 2)
    })

def list_courses():
    tid = int(get_jwt_identity())
    courses = Course.query.filter_by(teacher_id=tid).order_by(Course.id.desc()).all()
    
    result = []
    for c in courses:
        # Count enrollments for this course
        enrollment_count = Enrollment.query.filter_by(course_id=c.id).count()
        
        result.append({
            'id': c.id,
            'name': c.name,
            'description': c.description,
            'category': c.category,
            'duration': c.duration,
            'status': c.status or 'draft',
            'enrollment_count': enrollment_count
        })
    
    return jsonify(result)

def create_course(data: dict):
    tid = int(get_jwt_identity())
    new_course = Course(
        teacher_id=tid,
        name=data.get('name') or 'Untitled Course',
        description=data.get('description'),
        category=data.get('category'),
        duration=data.get('duration'),
        status=data.get('status') or 'draft'
    )
    db.session.add(new_course)
    db.session.commit()
    return jsonify({'message': 'Course created', 'id': new_course.id}), 201

def update_course(course_id: int, data: dict):
    tid = int(get_jwt_identity())
    course, error = _get_teacher_course(course_id, tid)
    if error:
        return error

    course.name = data.get('name', course.name)
    course.description = data.get('description', course.description)
    course.category = data.get('category', course.category)
    course.duration = data.get('duration', course.duration)
    db.session.commit()
    return jsonify({'message': 'Course updated'})

def delete_course(course_id: int):
    tid = int(get_jwt_identity())
    course, error = _get_teacher_course(course_id, tid)
    if error:
        return error
        
    db.session.delete(course)
    db.session.commit()
    return jsonify({'message': 'Course deleted'})

def toggle_course_status(course_id: int, status: str):
    tid = int(get_jwt_identity())
    course, error = _get_teacher_course(course_id, tid)
    if error:
        return error
    
    if status not in ['active', 'draft', 'archived']:
        return jsonify({'error': 'Invalid status provided'}), 400

    course.status = status
    db.session.commit()
    return jsonify({'message': 'Course status updated'})

def list_lessons(course_id: int):
    tid = int(get_jwt_identity())
    course, error = _get_teacher_course(course_id, tid)
    if error:
        return error

    # MS SQL Server doesn't support NULLS FIRST, use case statement instead
    from sqlalchemy import case
    lessons = Lesson.query.filter_by(course_id=course_id).order_by(
        case((Lesson.order_index == None, 1), else_=0),
        Lesson.order_index.asc(),
        Lesson.id.asc()
    ).all()
    return jsonify([{
        'id': l.id, 'title': l.title, 'description': l.description, 'video_url': l.video_url, 'order_index': l.order_index, 'content': l.content
    } for l in lessons])

def create_lesson(course_id: int, data: dict):
    tid = int(get_jwt_identity())
    course, error = _get_teacher_course(course_id, tid)
    if error:
        return error
        
    new_lesson = Lesson(
        course_id=course_id,
        title=data.get('title') or 'Untitled Lesson',
        description=data.get('description'),
        video_url=data.get('video_url'),
        content=data.get('content')
    )
    db.session.add(new_lesson)
    db.session.commit()
    return jsonify({'message': 'Lesson created', 'id': new_lesson.id}), 201

def update_lesson(lesson_id: int, data: dict):
    tid = int(get_jwt_identity())
    lesson, error = _get_teacher_lesson(lesson_id, tid)
    if error:
        return error

    for key in ('title', 'description', 'video_url', 'order_index', 'content'):
        if key in data:
            setattr(lesson, key, data[key])
    db.session.commit()
    return jsonify({'message': 'Lesson updated'})

def delete_lesson(lesson_id: int):
    tid = int(get_jwt_identity())
    lesson, error = _get_teacher_lesson(lesson_id, tid)
    if error:
        return error
        
    db.session.delete(lesson)
    db.session.commit()
    return jsonify({'message': 'Lesson deleted'})

def reorder_lessons(course_id: int, order: list[int]):
    tid = int(get_jwt_identity())
    course, error = _get_teacher_course(course_id, tid)
    if error:
        return error

    lessons = Lesson.query.filter_by(course_id=course_id).order_by(Lesson.id.asc()).all()
    if not lessons:
        return jsonify({'message': 'No lessons to reorder'})

    lesson_map = {l.id: l for l in lessons}
    if set(lesson_map.keys()) != set(order):
        return jsonify({'error': 'Order list must contain all and only all lesson IDs for the course'}), 400

    for i, lesson_id in enumerate(order):
        if lesson_map.get(lesson_id):
            lesson_map[lesson_id].order_index = i

    db.session.commit()
    return jsonify({'message': 'Lessons reordered'})

def list_quizzes(course_id: int):
    tid = int(get_jwt_identity())
    course, error = _get_teacher_course(course_id, tid)
    if error:
        return error
    
    quizzes = Quiz.query.filter_by(course_id=course_id).options(
        db.joinedload(Quiz.lesson),
        db.subqueryload(Quiz.questions)
    ).order_by(Quiz.id.desc()).all()
    
    return jsonify([{
        'id': q.id,
        'course_id': q.course_id,
        'lesson_id': q.lesson_id,
        'title': q.title,
        'description': q.description,
        'time_limit': q.time_limit,
        'created_at': q.created_at.isoformat() if q.created_at else '',
        'total_questions': len(q.questions),
        'lesson_title': q.lesson.title if q.lesson else None
    } for q in quizzes])

def list_all_quizzes_for_teacher():
    tid = int(get_jwt_identity())
    quizzes = Quiz.query.join(Course).filter(Course.teacher_id == tid).options(
        db.joinedload(Quiz.course),
        db.subqueryload(Quiz.questions)
    ).order_by(Quiz.id.desc()).all()
    
    return jsonify([{
        'id': q.id,
        'course_id': q.course_id,
        'title': q.title,
        'description': q.description,
        'time_limit': q.time_limit,
        'created_at': q.created_at.isoformat() if q.created_at else '',
        'total_questions': len(q.questions),
        'course_name': q.course.name if q.course else 'N/A'
    } for q in quizzes])

def create_quiz(course_id: int, data: dict):
    tid = int(get_jwt_identity())
    lesson_id = data.get('lesson_id')

    course, error = _get_teacher_course(course_id, tid)
    if error:
        return error

    # Validate lesson if provided
    if lesson_id:
        lesson = Lesson.query.filter_by(id=lesson_id, course_id=course_id).first()
        if not lesson:
            return jsonify({'error': 'Lesson not found in this course'}), 400

    new_quiz = Quiz(
        course_id=course_id,
        lesson_id=lesson_id if lesson_id else None,
        title=data.get('title') or 'New Quiz',
        description=data.get('description'),
        time_limit=data.get('time_limit')
    )
    db.session.add(new_quiz)
    db.session.commit()
    return jsonify({'message': 'Quiz created', 'id': new_quiz.id}), 201

def update_quiz(quiz_id: int, data: dict):
    tid = int(get_jwt_identity())
    quiz, error = _get_teacher_quiz(quiz_id, tid)
    if error:
        return error

    if 'lesson_id' in data:
        new_lesson_id = data['lesson_id']
        if new_lesson_id and new_lesson_id != quiz.lesson_id:
            lesson = Lesson.query.filter_by(id=new_lesson_id, course_id=quiz.course_id).first()
            if not lesson:
                return jsonify({'error': 'New lesson not found in this course'}), 400
        quiz.lesson_id = new_lesson_id if new_lesson_id else None

    quiz.title = data.get('title', quiz.title)
    quiz.description = data.get('description', quiz.description)
    quiz.time_limit = data.get('time_limit', quiz.time_limit)
    db.session.commit()
    return jsonify({'message': 'Quiz updated'})

def delete_quiz(quiz_id: int):
    tid = int(get_jwt_identity())
    quiz, error = _get_teacher_quiz(quiz_id, tid)
    if error:
        return error
        
    db.session.delete(quiz)
    db.session.commit()
    return jsonify({'message': 'Quiz deleted'})

def list_questions(quiz_id: int):
    """List all questions for a quiz"""
    tid = int(get_jwt_identity())
    quiz, error = _get_teacher_quiz(quiz_id, tid)
    if error:
        return error
    
    questions = QuizQuestion.query.filter_by(quiz_id=quiz_id).order_by(QuizQuestion.id.asc()).all()
    
    return jsonify([{
        'id': q.id,
        'question_text': q.question_text,
        'option_a': q.option_a,
        'option_b': q.option_b,
        'option_c': q.option_c,
        'option_d': q.option_d,
        'correct_option': q.correct_option
    } for q in questions])

def create_question(quiz_id: int, data: dict):
    tid = int(get_jwt_identity())
    quiz, error = _get_teacher_quiz(quiz_id, tid)
    if error:
        return error

    new_question = QuizQuestion(
        quiz_id=quiz_id,
        question_text=data.get('question_text'),
        option_a=data.get('option_a'),
        option_b=data.get('option_b'),
        option_c=data.get('option_c'),
        option_d=data.get('option_d'),
        correct_option=str(data.get('correct_option')).upper()[:1]
    )
    # Update total questions count on parent quiz
    quiz.total_questions = (quiz.total_questions or 0) + 1
    
    db.session.add(new_question)
    db.session.commit()
    return jsonify({'message': 'Question added', 'id': new_question.id}), 201

def update_question(question_id: int, data: dict):
    tid = int(get_jwt_identity())
    question = QuizQuestion.query.get(question_id)
    if not question:
        return jsonify({'error': 'Question not found'}), 404
        
    # Verify ownership via quiz
    quiz, error = _get_teacher_quiz(question.quiz_id, tid)
    if error:
        return error

    question.question_text = data.get('question_text', question.question_text)
    question.option_a = data.get('option_a', question.option_a)
    question.option_b = data.get('option_b', question.option_b)
    question.option_c = data.get('option_c', question.option_c)
    question.option_d = data.get('option_d', question.option_d)
    question.correct_option = str(data.get('correct_option', question.correct_option)).upper()[:1]
    db.session.commit()
    return jsonify({'message': 'Question updated'})

def delete_question(question_id: int):
    tid = int(get_jwt_identity())
    question = QuizQuestion.query.options(db.joinedload(QuizQuestion.quiz)).get(question_id)
    if not question:
        return jsonify({'message': 'Question deleted'}), 200 # Idempotent

    # Verify ownership via quiz
    if question.quiz.course.teacher_id != tid:
        return jsonify({'error': 'You do not have permission for this quiz'}), 403
    
    # Update total questions count on parent quiz
    quiz = question.quiz
    quiz.total_questions = max(0, (quiz.total_questions or 1) - 1)

    db.session.delete(question)
    db.session.commit()
    return jsonify({'message': 'Question deleted'})

def list_quiz_results(quiz_id: int):
    tid = int(get_jwt_identity())
    quiz, error = _get_teacher_quiz(quiz_id, tid)
    if error:
        return error

    results = QuizResult.query.filter_by(quiz_id=quiz_id).options(
        db.joinedload(QuizResult.user)
    ).order_by(QuizResult.submitted_at.desc()).all()
    
    return jsonify([{
        'user_id': r.user_id,
        'user_name': r.user.fullname if r.user else 'N/A',
        'score': r.score,
        'submitted_at': r.submitted_at.isoformat() if r.submitted_at else ''
    } for r in results])

def list_course_scores(course_id: int):
    tid = int(get_jwt_identity())
    course, error = _get_teacher_course(course_id, tid)
    if error:
        return error

    results = db.session.query(QuizResult).join(Quiz).filter(Quiz.course_id == course_id).options(
        db.joinedload(QuizResult.user),
        db.joinedload(QuizResult.quiz).joinedload(Quiz.lesson)
    ).order_by(QuizResult.submitted_at.desc()).all()
    
    items = [{
        'user_id': r.user_id,
        'user_name': r.user.fullname if r.user else 'N/A',
        'score': r.score,
        'submitted_at': r.submitted_at.isoformat() if r.submitted_at else '',
        'quiz_id': r.quiz_id,
        'quiz_title': r.quiz.title if r.quiz else 'N/A',
        'lesson_id': r.quiz.lesson_id if r.quiz else None,
        'lesson_title': r.quiz.lesson.title if r.quiz and r.quiz.lesson else None
    } for r in results]
    
    student_ids = {item['user_id'] for item in items if item['user_id'] is not None}
    quiz_ids = {item['quiz_id'] for item in items if item['quiz_id'] is not None}
    avg_score = round(sum(item['score'] for item in items) / len(items), 2) if items else 0.0

    return jsonify({
        'course_id': course_id,
        'course_name': course.name,
        'results': items,
        'summary': {
            'students': len(student_ids),
            'quizzes': len(quiz_ids),
            'attempts': len(items),
            'average_score': avg_score
        }
    })

def list_subscribers(course_id: int):
    tid = int(get_jwt_identity())
    course, error = _get_teacher_course(course_id, tid)
    if error:
        return error
        
    enrollments = Enrollment.query.filter_by(course_id=course_id).options(
        db.joinedload(Enrollment.student)
    ).order_by(Enrollment.id.desc()).all()
    
    return jsonify([{
        'id': e.id,
        'user_id': e.student_id,
        'fullname': e.student.fullname if e.student else 'N/A',
        'email': e.student.email if e.student else 'N/A',
        'status': e.status
    } for e in enrollments])

def get_student_progress(course_id: int, student_id: int):
    """Get progress for a specific student in a course"""
    from app.models.progress_model import Progress
    
    tid = int(get_jwt_identity())
    course, error = _get_teacher_course(course_id, tid)
    if error:
        return error
    
    # Check if student is enrolled
    enrollment = Enrollment.query.filter_by(
        course_id=course_id,
        student_id=student_id
    ).first()
    
    if not enrollment:
        return jsonify({'error': 'Student not enrolled in this course'}), 404
    
    # Get progress data
    progress = Progress.query.filter_by(
        course_id=course_id,
        student_id=student_id
    ).first()
    
    if not progress:
        # Return default progress if not found
        return jsonify({
            'lessons_completed': 0,
            'total_lessons': 0,
            'progress_percent': 0
        })
    
    return jsonify({
        'lessons_completed': progress.lessons_completed or 0,
        'total_lessons': progress.total_lessons or 0,
        'progress_percent': progress.progress_percent or 0,
        'last_updated': progress.last_updated.isoformat() if progress.last_updated else None
    })

def approve_subscriber(enroll_id: int):
    tid = int(get_jwt_identity())
    enrollment = Enrollment.query.options(db.joinedload(Enrollment.course)).get(enroll_id)
    if not enrollment:
        return jsonify({'error': 'Enrollment not found'}), 404
    if enrollment.course.teacher_id != tid:
        return jsonify({'error': 'You do not have permission for this course'}), 403

    enrollment.status = 'approved'
    db.session.commit()
    return jsonify({'message': 'Enrollment approved'})

def reject_subscriber(enroll_id: int):
    tid = int(get_jwt_identity())
    enrollment = Enrollment.query.options(db.joinedload(Enrollment.course)).get(enroll_id)
    if not enrollment:
        return jsonify({'error': 'Enrollment not found'}), 404
    if enrollment.course.teacher_id != tid:
        return jsonify({'error': 'You do not have permission for this course'}), 403

    enrollment.status = 'rejected'
    db.session.commit()
    return jsonify({'message': 'Enrollment rejected'})

def remove_subscriber(enroll_id: int):
    tid = int(get_jwt_identity())
    enrollment = Enrollment.query.options(db.joinedload(Enrollment.course)).get(enroll_id)
    if not enrollment:
        return jsonify({'error': 'Enrollment not found'}), 404 # or 200 for idempotency
    if enrollment.course.teacher_id != tid:
        return jsonify({'error': 'You do not have permission for this course'}), 403
    
    db.session.delete(enrollment)
    db.session.commit()
    return jsonify({'message': 'Subscriber removed'})

def import_quiz_questions(quiz_id: int, file_path: str):
    """Import questions from uploaded Word file"""
    import requests
    import tempfile
    from flask import current_app
    
    current_app.logger.info(f"[QuizImport] Importing questions for quiz {quiz_id} from: {file_path}")
    
    if not file_path:
        current_app.logger.error("[QuizImport] file_path is empty or None")
        return jsonify({'error': 'file_path is required'}), 400
    
    tid = int(get_jwt_identity())
    quiz, error = _get_teacher_quiz(quiz_id, tid)
    if error:
        return error
    
    # Check if file_path is a URL (Cloudinary) or local path
    if file_path.startswith('http://') or file_path.startswith('https://'):
        # Download from URL (Cloudinary)
        try:
            current_app.logger.info(f"[QuizImport] Downloading from Cloudinary: {file_path}")
            response = requests.get(file_path, timeout=30)
            response.raise_for_status()
            
            current_app.logger.info(f"[QuizImport] Downloaded {len(response.content)} bytes")
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
                tmp_file.write(response.content)
                full_path = tmp_file.name
            
            current_app.logger.info(f"[QuizImport] Saved to temp file: {full_path}")
        except Exception as e:
            current_app.logger.error(f"[QuizImport] Download failed: {str(e)}")
            return jsonify({'error': f'Failed to download file from cloud: {str(e)}'}), 400
    else:
        # Local file path
        upload_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads')
        full_path = os.path.join(upload_folder, file_path)
        
        if not os.path.exists(full_path):
            return jsonify({'error': 'Uploaded file not found'}), 404
    
    # Parse questions from Word file
    current_app.logger.info(f"[QuizImport] Parsing document: {full_path}")
    result = parse_quiz_from_docx(full_path)
    
    current_app.logger.info(f"[QuizImport] Parse result: success={result['success']}, count={result.get('count', 0)}")
    
    if not result['success']:
        error_msg = result.get('error', 'Failed to parse document')
        current_app.logger.error(f"[QuizImport] Parse failed: {error_msg}")
        return jsonify({'error': error_msg}), 400
    
    if not result['questions']:
        current_app.logger.warning("[QuizImport] No valid questions found in document")
        return jsonify({'error': 'No valid questions found in document. Please check the format.'}), 400
    
    # Add questions to database
    added_count = 0
    for q_data in result['questions']:
        new_question = QuizQuestion(
            quiz_id=quiz_id,
            question_text=q_data['question_text'],
            option_a=q_data['option_a'],
            option_b=q_data['option_b'],
            option_c=q_data['option_c'],
            option_d=q_data['option_d'],
            correct_option=q_data['correct_option']
        )
        db.session.add(new_question)
        added_count += 1
    
    # Update total questions count
    quiz.total_questions = (quiz.total_questions or 0) + added_count
    
    db.session.commit()
    
    # Cleanup temp file if it was downloaded
    if file_path.startswith('http://') or file_path.startswith('https://'):
        try:
            os.unlink(full_path)
        except:
            pass
    
    return jsonify({
        'message': f'Successfully imported {added_count} questions',
        'count': added_count,
        'file_path': file_path
    }), 201
