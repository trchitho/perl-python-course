"""
Upload Controller
Handles file upload requests with Cloudinary or local storage
"""
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.services.file_upload_service import (
    process_upload, delete_file, get_upload_stats,
    MAX_FILE_SIZE, MAX_IMAGE_SIZE, MAX_VIDEO_SIZE, MAX_DOCUMENT_SIZE
)
from app.services import cloudinary_service
import logging

logger = logging.getLogger(__name__)


def upload_file():
    """
    Upload file with validation
    Uses Cloudinary for videos/images if configured, otherwise local storage
    """
    user_id = get_jwt_identity()
    
    # Check if file is present
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Get optional parameters
    subfolder = request.form.get('subfolder', 'general')
    compress = request.form.get('compress', 'true').lower() == 'true'
    
    # Determine file type
    file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    video_exts = ['mp4', 'avi', 'mov', 'wmv', 'webm', 'flv']
    image_exts = ['jpg', 'jpeg', 'png', 'gif', 'webp']
    document_exts = ['pdf', 'doc', 'docx', 'ppt', 'pptx']
    
    # Use Cloudinary for videos and images if configured
    if cloudinary_service.is_enabled():
        file.seek(0)
        file_data = file.read()
        
        if file_ext in video_exts:
            # Upload video to Cloudinary
            result = cloudinary_service.upload_video(file_data, file.filename, f'elearning/{subfolder}')
        elif file_ext in image_exts:
            # Upload image to Cloudinary
            result = cloudinary_service.upload_image(file_data, file.filename, f'elearning/{subfolder}')
        elif file_ext in document_exts:
            # Upload document to Cloudinary
            result = cloudinary_service.upload_document(file_data, file.filename, f'elearning/{subfolder}')
        else:
            # Fallback to local for other files
            file.seek(0)
            result = process_upload(file, subfolder, compress)
            if result['success']:
                result['url'] = f"/uploads/{result['path']}"
                result['storage'] = 'local'
        
        if result['success']:
            logger.info(f"[Upload] User {user_id} uploaded to Cloudinary: {result.get('public_id', file.filename)}")
            # Ensure path is set for compatibility - prefer secure_url (https)
            if 'path' not in result:
                result['path'] = result.get('secure_url') or result.get('url')
            return jsonify({
                **result,
                'storage': 'cloudinary'
            }), 200
        else:
            return jsonify(result), 400
    else:
        # Fallback to local storage
        result = process_upload(file, subfolder, compress)
        
        if result['success']:
            logger.info(f"[Upload] User {user_id} uploaded locally: {result['filename']}")
            result['url'] = f"/uploads/{result['path']}"
            result['storage'] = 'local'
            return jsonify(result), 200
        else:
            return jsonify(result), 400


def upload_lesson_material():
    """Upload lesson material (teacher only)"""
    user_id = get_jwt_identity()
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    lesson_id = request.form.get('lesson_id')
    
    if not lesson_id:
        return jsonify({'error': 'lesson_id is required'}), 400
    
    # Process upload to lessons subfolder
    result = process_upload(file, f'lessons/{lesson_id}', compress=True)
    
    if result['success']:
        logger.info(f"[Upload] Teacher {user_id} uploaded material for lesson {lesson_id}")
        return jsonify(result), 200
    else:
        return jsonify(result), 400


def delete_uploaded_file():
    """Delete uploaded file"""
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    
    file_path = data.get('file_path')
    
    if not file_path:
        return jsonify({'error': 'file_path is required'}), 400
    
    success = delete_file(file_path)
    
    if success:
        logger.info(f"[Upload] User {user_id} deleted: {file_path}")
        return jsonify({'message': 'File deleted successfully'}), 200
    else:
        return jsonify({'error': 'File not found or deletion failed'}), 404


def get_upload_limits():
    """Get upload size limits"""
    return jsonify({
        'max_file_size': MAX_FILE_SIZE,
        'max_image_size': MAX_IMAGE_SIZE,
        'max_video_size': MAX_VIDEO_SIZE,
        'max_document_size': MAX_DOCUMENT_SIZE,
        'max_file_size_mb': MAX_FILE_SIZE / (1024 * 1024),
        'max_image_size_mb': MAX_IMAGE_SIZE / (1024 * 1024),
        'max_video_size_mb': MAX_VIDEO_SIZE / (1024 * 1024),
        'max_document_size_mb': MAX_DOCUMENT_SIZE / (1024 * 1024)
    }), 200


def get_stats():
    """Get upload statistics (admin only)"""
    local_stats = get_upload_stats()
    cloudinary_stats = cloudinary_service.get_storage_stats()
    
    return jsonify({
        'local_storage': local_stats,
        'cloudinary': cloudinary_stats
    }), 200
