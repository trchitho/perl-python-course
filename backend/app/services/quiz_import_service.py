"""
Quiz Import Service
Parse Word documents to extract quiz questions
"""
import os
import re
from docx import Document
import logging

logger = logging.getLogger(__name__)

def parse_quiz_from_docx(file_path):
    """
    Parse quiz questions from Word document
    
    Expected format:
    Question 1: What is Python?
    A. A snake
    B. A programming language
    C. A framework
    D. A database
    Answer: B
    
    Returns list of questions with format:
    [{
        'question_text': str,
        'option_a': str,
        'option_b': str,
        'option_c': str,
        'option_d': str,
        'correct_option': str
    }]
    """
    try:
        doc = Document(file_path)
        questions = []
        current_question = None
        
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue
            
            # Check for question (starts with "Question" or number)
            question_match = re.match(r'^(?:Question\s+)?(\d+)[:.)\s]+(.+)', text, re.IGNORECASE)
            if question_match:
                # Save previous question if exists
                if current_question and _is_valid_question(current_question):
                    questions.append(current_question)
                
                # Start new question
                current_question = {
                    'question_text': question_match.group(2).strip(),
                    'option_a': '',
                    'option_b': '',
                    'option_c': '',
                    'option_d': '',
                    'correct_option': ''
                }
                continue
            
            if not current_question:
                continue
            
            # Check for options (A, B, C, D)
            option_match = re.match(r'^([A-Da-d])[:.)\s]+(.+)', text)
            if option_match:
                option_letter = option_match.group(1).upper()
                option_text = option_match.group(2).strip()
                
                if option_letter == 'A':
                    current_question['option_a'] = option_text
                elif option_letter == 'B':
                    current_question['option_b'] = option_text
                elif option_letter == 'C':
                    current_question['option_c'] = option_text
                elif option_letter == 'D':
                    current_question['option_d'] = option_text
                continue
            
            # Check for answer
            answer_match = re.match(r'^(?:Answer|Correct|Đáp án)[:.)\s]+([A-Da-d])', text, re.IGNORECASE)
            if answer_match:
                current_question['correct_option'] = answer_match.group(1).upper()
                continue
        
        # Add last question
        if current_question and _is_valid_question(current_question):
            questions.append(current_question)
        
        logger.info(f"[QuizImport] Parsed {len(questions)} questions from {file_path}")
        return {
            'success': True,
            'questions': questions,
            'count': len(questions)
        }
    
    except Exception as e:
        logger.error(f"[QuizImport] Error parsing document: {e}")
        return {
            'success': False,
            'error': str(e),
            'questions': []
        }


def _is_valid_question(question):
    """Validate question has all required fields"""
    return (
        question.get('question_text') and
        question.get('option_a') and
        question.get('option_b') and
        question.get('option_c') and
        question.get('option_d') and
        question.get('correct_option') in ['A', 'B', 'C', 'D']
    )


def parse_quiz_from_text(text_content):
    """
    Parse quiz questions from plain text
    Alternative format for copy-paste
    """
    questions = []
    lines = text_content.split('\n')
    current_question = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check for question
        question_match = re.match(r'^(?:Question\s+)?(\d+)[:.)\s]+(.+)', line, re.IGNORECASE)
        if question_match:
            if current_question and _is_valid_question(current_question):
                questions.append(current_question)
            
            current_question = {
                'question_text': question_match.group(2).strip(),
                'option_a': '',
                'option_b': '',
                'option_c': '',
                'option_d': '',
                'correct_option': ''
            }
            continue
        
        if not current_question:
            continue
        
        # Check for options
        option_match = re.match(r'^([A-Da-d])[:.)\s]+(.+)', line)
        if option_match:
            option_letter = option_match.group(1).upper()
            option_text = option_match.group(2).strip()
            
            if option_letter == 'A':
                current_question['option_a'] = option_text
            elif option_letter == 'B':
                current_question['option_b'] = option_text
            elif option_letter == 'C':
                current_question['option_c'] = option_text
            elif option_letter == 'D':
                current_question['option_d'] = option_text
            continue
        
        # Check for answer
        answer_match = re.match(r'^(?:Answer|Correct|Đáp án)[:.)\s]+([A-Da-d])', line, re.IGNORECASE)
        if answer_match:
            current_question['correct_option'] = answer_match.group(1).upper()
            continue
    
    # Add last question
    if current_question and _is_valid_question(current_question):
        questions.append(current_question)
    
    return {
        'success': True,
        'questions': questions,
        'count': len(questions)
    }
