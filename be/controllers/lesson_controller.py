import os
from flask import request, jsonify
from models.lesson_model import Lesson
from extensions import db
from werkzeug.utils import secure_filename
import docx
import PyPDF2

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'docx', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_docx(filepath):
    doc = docx.Document(filepath)
    return '\n'.join([para.text for para in doc.paragraphs])

def extract_text_from_pdf(filepath):
    with open(filepath, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        return '\n'.join(page.extract_text() for page in reader.pages)

def add_lesson_from_file():
    if 'file' not in request.files or 'course_id' not in request.form:
        return jsonify({"error": "Missing file or course_id"}), 400

    file = request.files['file']
    course_id = request.form['course_id']

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        if filename.endswith('.docx'):
            content = extract_text_from_docx(filepath)
        elif filename.endswith('.pdf'):
            content = extract_text_from_pdf(filepath)
        else:
            return jsonify({"error": "Unsupported file type"}), 400

        title = filename.rsplit('.', 1)[0]  # lấy tên file làm title

        new_lesson = Lesson(title=title, content=content, course_id=course_id)
        db.session.add(new_lesson)
        db.session.commit()

        return jsonify({"message": "Lesson added successfully"}), 201

    return jsonify({"error": "Invalid file"}), 400
