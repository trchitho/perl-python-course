"""
Create test data for Teacher Dashboard
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user_model import User
from app.models.course_model import Course
from app.models.lesson_model import Lesson
from app.models.quiz_model import Quiz, QuizQuestion, QuizResult
from app.models.enrollment_model import Enrollment

def create_test_data():
    app = create_app()
    
    with app.app_context():
        print("🎯 Creating test data for Teacher Dashboard...")
        
        # Find or create teacher
        teacher = User.query.filter_by(email='teacher1@test.com').first()
        if not teacher:
            teacher = User(
                fullname='Teacher One',
                email='teacher1@test.com',
                role='teacher'
            )
            teacher.set_password('password123')
            db.session.add(teacher)
            db.session.commit()
            print(f"✅ Created teacher: {teacher.email}")
        else:
            print(f"✅ Found existing teacher: {teacher.email}")
        
        # Create courses
        courses_data = [
            {'name': 'Python Programming', 'description': 'Learn Python from scratch', 'category': 'Programming'},
            {'name': 'Web Development', 'description': 'HTML, CSS, JavaScript', 'category': 'Web'},
            {'name': 'Database Design', 'description': 'SQL and Database concepts', 'category': 'Database'},
        ]
        
        courses = []
        for course_data in courses_data:
            course = Course.query.filter_by(
                teacher_id=teacher.id,
                name=course_data['name']
            ).first()
            
            if not course:
                course = Course(
                    teacher_id=teacher.id,
                    name=course_data['name'],
                    description=course_data['description'],
                    category=course_data['category'],
                    status='published'
                )
                db.session.add(course)
                db.session.commit()
                print(f"✅ Created course: {course.name}")
            else:
                print(f"✅ Found existing course: {course.name}")
            
            courses.append(course)
        
        # Create lessons for each course
        for course in courses:
            existing_lessons = Lesson.query.filter_by(course_id=course.id).count()
            if existing_lessons == 0:
                for i in range(1, 4):  # 3 lessons per course
                    lesson = Lesson(
                        course_id=course.id,
                        title=f'{course.name} - Lesson {i}',
                        content=f'Content for lesson {i}',
                        description=f'Description for lesson {i}',
                        order_index=i
                    )
                    db.session.add(lesson)
                print(f"✅ Created 3 lessons for: {course.name}")
            else:
                print(f"✅ Found {existing_lessons} lessons for: {course.name}")
        
        db.session.commit()
        
        # Create quizzes
        for course in courses:
            existing_quizzes = Quiz.query.filter_by(course_id=course.id).count()
            if existing_quizzes == 0:
                quiz = Quiz(
                    course_id=course.id,
                    title=f'{course.name} Quiz',
                    description=f'Test your knowledge of {course.name}',
                    time_limit=30
                )
                db.session.add(quiz)
                db.session.commit()
                
                # Add questions
                for i in range(1, 6):  # 5 questions per quiz
                    question = QuizQuestion(
                        quiz_id=quiz.id,
                        question_text=f'Question {i} for {course.name}?',
                        option_a='Option A',
                        option_b='Option B',
                        option_c='Option C',
                        option_d='Option D',
                        correct_option='A'
                    )
                    db.session.add(question)
                
                print(f"✅ Created quiz with 5 questions for: {course.name}")
            else:
                print(f"✅ Found {existing_quizzes} quizzes for: {course.name}")
        
        db.session.commit()
        
        # Create students and enrollments
        students_data = [
            {'name': 'Student One', 'email': 'student1@test.com'},
            {'name': 'Student Two', 'email': 'student2@test.com'},
            {'name': 'Student Three', 'email': 'student3@test.com'},
            {'name': 'Student Four', 'email': 'student4@test.com'},
            {'name': 'Student Five', 'email': 'student5@test.com'},
        ]
        
        students = []
        for student_data in students_data:
            student = User.query.filter_by(email=student_data['email']).first()
            if not student:
                student = User(
                    fullname=student_data['name'],
                    email=student_data['email'],
                    role='student'
                )
                student.set_password('password123')
                db.session.add(student)
                db.session.commit()
                print(f"✅ Created student: {student.email}")
            else:
                print(f"✅ Found existing student: {student.email}")
            
            students.append(student)
        
        # Enroll students in courses
        for student in students:
            for course in courses:
                enrollment = Enrollment.query.filter_by(
                    student_id=student.id,
                    course_id=course.id
                ).first()
                
                if not enrollment:
                    enrollment = Enrollment(
                        student_id=student.id,
                        course_id=course.id,
                        status='approved'
                    )
                    db.session.add(enrollment)
        
        db.session.commit()
        print(f"✅ Enrolled {len(students)} students in {len(courses)} courses")
        
        # Create quiz results
        for student in students:
            for course in courses:
                quiz = Quiz.query.filter_by(course_id=course.id).first()
                if quiz:
                    result = QuizResult.query.filter_by(
                        user_id=student.id,
                        quiz_id=quiz.id
                    ).first()
                    
                    if not result:
                        # Random score between 60-100
                        import random
                        score = random.randint(60, 100)
                        
                        result = QuizResult(
                            user_id=student.id,
                            quiz_id=quiz.id,
                            score=score
                        )
                        db.session.add(result)
        
        db.session.commit()
        print(f"✅ Created quiz results for students")
        
        print("\n" + "=" * 70)
        print("✅ TEST DATA CREATED SUCCESSFULLY!")
        print("=" * 70)
        print(f"\n📊 Summary:")
        print(f"   • Teacher: {teacher.email} / password123")
        print(f"   • Courses: {len(courses)}")
        print(f"   • Lessons: {Lesson.query.join(Course).filter(Course.teacher_id == teacher.id).count()}")
        print(f"   • Quizzes: {Quiz.query.join(Course).filter(Course.teacher_id == teacher.id).count()}")
        print(f"   • Students: {len(students)}")
        print(f"   • Enrollments: {Enrollment.query.join(Course).filter(Course.teacher_id == teacher.id).count()}")
        print(f"\n🎯 Login as teacher:")
        print(f"   Email: teacher1@test.com")
        print(f"   Password: password123")
        print("=" * 70 + "\n")

if __name__ == '__main__':
    create_test_data()
