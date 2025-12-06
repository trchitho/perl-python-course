"""
Placement Test Controller
Handles placement test logic, scoring, and recommendations
"""
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity
from app import db
from app.models.placement_test_model import PlacementTest
from sqlalchemy import text
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Scoring thresholds for recommendations
LEVEL_THRESHOLDS = {
    'Beginner': (0, 30),      # 0-30 points
    'Intermediate': (31, 45),  # 31-45 points
    'Advanced': (46, 60)       # 46-60 points
}


def get_questions():
    """
    Get placement test questions
    Returns 30 questions (10 from each difficulty level)
    """
    try:
        if db.get_engine().dialect.name == 'mssql':
            # Get questions from database
            query = text("""
                SELECT 
                    QuestionID,
                    QuestionText,
                    OptionA,
                    OptionB,
                    OptionC,
                    OptionD,
                    Difficulty,
                    Category,
                    Points
                FROM PlacementTestQuestions
                ORDER BY Difficulty, QuestionID
            """)
            
            rows = db.session.execute(query).fetchall()
            
            questions = []
            for row in rows:
                questions.append({
                    'id': row[0],
                    'question': row[1],
                    'options': {
                        'A': row[2],
                        'B': row[3],
                        'C': row[4],
                        'D': row[5]
                    },
                    'difficulty': row[6],
                    'category': row[7],
                    'points': row[8]
                })
            
            return jsonify({
                'questions': questions,
                'total_questions': len(questions),
                'total_points': sum(q['points'] for q in questions),
                'time_limit': 30  # 30 minutes
            }), 200
        
        return jsonify({'error': 'Database not supported'}), 500
    
    except Exception as e:
        logger.error(f"[PlacementTest] Error getting questions: {e}")
        return jsonify({'error': str(e)}), 500


def submit_test():
    """
    Submit placement test and calculate score
    """
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    
    answers = data.get('answers', {})  # {question_id: answer}
    
    if not answers:
        return jsonify({'error': 'No answers provided'}), 400
    
    try:
        # Get correct answers from database
        if db.get_engine().dialect.name == 'mssql':
            query = text("""
                SELECT QuestionID, CorrectAnswer, Points
                FROM PlacementTestQuestions
            """)
            
            rows = db.session.execute(query).fetchall()
            
            # Calculate score
            total_score = 0
            correct_count = 0
            total_questions = len(rows)
            
            results = []
            
            for row in rows:
                question_id = str(row[0])
                correct_answer = row[1]
                points = row[2]
                
                user_answer = answers.get(question_id, '')
                is_correct = user_answer.upper() == correct_answer.upper()
                
                if is_correct:
                    total_score += points
                    correct_count += 1
                
                results.append({
                    'question_id': question_id,
                    'user_answer': user_answer,
                    'correct_answer': correct_answer,
                    'is_correct': is_correct,
                    'points_earned': points if is_correct else 0
                })
            
            # Determine recommended level
            recommended_level = determine_level(total_score)
            
            # Save to database
            placement_test = PlacementTest(
                user_id=user_id,
                score=total_score,
                recommended_level=recommended_level,
                taken_at=datetime.utcnow()
            )
            
            db.session.add(placement_test)
            db.session.commit()
            
            logger.info(f"[PlacementTest] User {user_id} scored {total_score}/60 - Level: {recommended_level}")
            
            return jsonify({
                'test_id': placement_test.id,
                'score': float(total_score),
                'max_score': 60,
                'percentage': round((total_score / 60) * 100, 2),
                'correct_answers': correct_count,
                'total_questions': total_questions,
                'recommended_level': recommended_level,
                'recommendation': get_recommendation(recommended_level),
                'results': results
            }), 200
        
        return jsonify({'error': 'Database not supported'}), 500
    
    except Exception as e:
        logger.error(f"[PlacementTest] Error submitting test: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


def determine_level(score):
    """Determine recommended level based on score"""
    for level, (min_score, max_score) in LEVEL_THRESHOLDS.items():
        if min_score <= score <= max_score:
            return level
    return 'Beginner'


def get_recommendation(level):
    """Get learning recommendation based on level"""
    recommendations = {
        'Beginner': {
            'title': 'Beginner Level',
            'description': 'Bạn nên bắt đầu với các khóa học cơ bản về máy tính và lập trình.',
            'suggested_courses': [
                'Nhập môn Tin học',
                'Cơ bản về máy tính',
                'HTML & CSS cơ bản',
                'Lập trình căn bản'
            ],
            'learning_path': 'Bắt đầu từ những kiến thức nền tảng, học cách sử dụng máy tính và các công cụ cơ bản.',
            'estimated_time': '3-6 tháng'
        },
        'Intermediate': {
            'title': 'Intermediate Level',
            'description': 'Bạn đã có kiến thức cơ bản tốt. Hãy nâng cao kỹ năng lập trình và công nghệ web.',
            'suggested_courses': [
                'JavaScript nâng cao',
                'Backend Development',
                'Database Design',
                'Git & GitHub'
            ],
            'learning_path': 'Tập trung vào lập trình web, database và các công cụ phát triển chuyên nghiệp.',
            'estimated_time': '6-12 tháng'
        },
        'Advanced': {
            'title': 'Advanced Level',
            'description': 'Bạn có kiến thức vững vàng. Hãy học các chủ đề nâng cao và chuyên sâu.',
            'suggested_courses': [
                'Microservices Architecture',
                'DevOps & CI/CD',
                'Cloud Computing',
                'System Design'
            ],
            'learning_path': 'Chuyên sâu vào kiến trúc hệ thống, cloud, và các công nghệ tiên tiến.',
            'estimated_time': '12+ tháng'
        }
    }
    
    return recommendations.get(level, recommendations['Beginner'])


def get_user_test_history():
    """Get user's placement test history"""
    user_id = int(get_jwt_identity())
    
    try:
        if db.get_engine().dialect.name == 'mssql':
            query = text("""
                SELECT TestID, Score, RecommendedLevel, TakenAt
                FROM PlacementTests
                WHERE UserID = :user_id
                ORDER BY TakenAt DESC
            """)
            
            rows = db.session.execute(query, {'user_id': user_id}).fetchall()
            
            history = []
            for row in rows:
                history.append({
                    'test_id': row[0],
                    'score': float(row[1]),
                    'recommended_level': row[2],
                    'taken_at': row[3].isoformat() if row[3] else None
                })
            
            return jsonify({
                'history': history,
                'total_tests': len(history)
            }), 200
        
        return jsonify({'error': 'Database not supported'}), 500
    
    except Exception as e:
        logger.error(f"[PlacementTest] Error getting history: {e}")
        return jsonify({'error': str(e)}), 500


def get_test_result(test_id):
    """Get specific test result"""
    user_id = int(get_jwt_identity())
    
    try:
        if db.get_engine().dialect.name == 'mssql':
            query = text("""
                SELECT TestID, Score, RecommendedLevel, TakenAt
                FROM PlacementTests
                WHERE TestID = :test_id AND UserID = :user_id
            """)
            
            row = db.session.execute(query, {
                'test_id': test_id,
                'user_id': user_id
            }).fetchone()
            
            if not row:
                return jsonify({'error': 'Test not found'}), 404
            
            score = float(row[1])
            level = row[2]
            
            return jsonify({
                'test_id': row[0],
                'score': score,
                'max_score': 60,
                'percentage': round((score / 60) * 100, 2),
                'recommended_level': level,
                'recommendation': get_recommendation(level),
                'taken_at': row[3].isoformat() if row[3] else None
            }), 200
        
        return jsonify({'error': 'Database not supported'}), 500
    
    except Exception as e:
        logger.error(f"[PlacementTest] Error getting result: {e}")
        return jsonify({'error': str(e)}), 500
