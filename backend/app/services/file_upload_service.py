"""
File Upload Service
Handles file uploads with compression, validation, and progress tracking
"""
import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads')
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100MB
MAX_DOCUMENT_SIZE = 20 * 1024 * 1024  # 20MB

ALLOWED_EXTENSIONS = {
    'image': {'png', 'jpg', 'jpeg', 'gif', 'webp'},
    'video': {'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm'},
    'document': {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt', 'md'},
    'archive': {'zip', 'rar', '7z', 'tar', 'gz'}
}

# Image compression settings
IMAGE_QUALITY = 85
IMAGE_MAX_WIDTH = 1920
IMAGE_MAX_HEIGHT = 1080


def ensure_upload_folder():
    """Ensure upload folder exists"""
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
        logger.info(f"[Upload] Created upload folder: {UPLOAD_FOLDER}")


def get_file_extension(filename):
    """Get file extension"""
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''


def get_file_type(filename):
    """Determine file type from extension"""
    ext = get_file_extension(filename)
    
    for file_type, extensions in ALLOWED_EXTENSIONS.items():
        if ext in extensions:
            return file_type
    
    return 'unknown'


def is_allowed_file(filename):
    """Check if file extension is allowed"""
    ext = get_file_extension(filename)
    
    for extensions in ALLOWED_EXTENSIONS.values():
        if ext in extensions:
            return True
    
    return False


def validate_file_size(file_size, file_type):
    """Validate file size based on type"""
    limits = {
        'image': MAX_IMAGE_SIZE,
        'video': MAX_VIDEO_SIZE,
        'document': MAX_DOCUMENT_SIZE,
        'archive': MAX_FILE_SIZE
    }
    
    max_size = limits.get(file_type, MAX_FILE_SIZE)
    
    if file_size > max_size:
        return False, f"File too large. Max size for {file_type}: {max_size / (1024*1024):.0f}MB"
    
    return True, "OK"


def compress_image(file_data, filename):
    """Compress image file"""
    try:
        # Open image
        img = Image.open(io.BytesIO(file_data))
        
        # Convert RGBA to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Resize if too large
        if img.width > IMAGE_MAX_WIDTH or img.height > IMAGE_MAX_HEIGHT:
            img.thumbnail((IMAGE_MAX_WIDTH, IMAGE_MAX_HEIGHT), Image.Resampling.LANCZOS)
            logger.info(f"[Upload] Resized image: {filename}")
        
        # Compress
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=IMAGE_QUALITY, optimize=True)
        compressed_data = output.getvalue()
        
        # Calculate compression ratio
        original_size = len(file_data)
        compressed_size = len(compressed_data)
        ratio = (1 - compressed_size / original_size) * 100
        
        logger.info(f"[Upload] Compressed {filename}: {original_size/1024:.1f}KB → {compressed_size/1024:.1f}KB ({ratio:.1f}% reduction)")
        
        return compressed_data, f"{os.path.splitext(filename)[0]}.jpg"
    
    except Exception as e:
        logger.error(f"[Upload] Image compression failed: {e}")
        return file_data, filename


def generate_unique_filename(original_filename):
    """Generate unique filename"""
    ext = get_file_extension(original_filename)
    unique_id = str(uuid.uuid4())
    return f"{unique_id}.{ext}"


def save_file(file_data, filename, subfolder='general'):
    """Save file to disk"""
    ensure_upload_folder()
    
    # Create subfolder if needed
    target_folder = os.path.join(UPLOAD_FOLDER, subfolder)
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    
    # Generate unique filename
    unique_filename = generate_unique_filename(filename)
    file_path = os.path.join(target_folder, unique_filename)
    
    # Save file
    with open(file_path, 'wb') as f:
        f.write(file_data)
    
    logger.info(f"[Upload] Saved file: {file_path}")
    
    # Return relative path
    return os.path.join(subfolder, unique_filename)


def process_upload(file, subfolder='general', compress=True):
    """
    Process file upload with validation and compression
    
    Returns:
        dict: {
            'success': bool,
            'filename': str,
            'path': str,
            'size': int,
            'type': str,
            'compressed': bool,
            'message': str
        }
    """
    try:
        # Get filename
        original_filename = secure_filename(file.filename)
        
        # Validate extension
        if not is_allowed_file(original_filename):
            return {
                'success': False,
                'message': f'File type not allowed. Allowed: {", ".join([ext for exts in ALLOWED_EXTENSIONS.values() for ext in exts])}'
            }
        
        # Read file data
        file.seek(0)
        file_data = file.read()
        file_size = len(file_data)
        
        # Determine file type
        file_type = get_file_type(original_filename)
        
        # Validate size
        valid, message = validate_file_size(file_size, file_type)
        if not valid:
            return {
                'success': False,
                'message': message
            }
        
        # Compress if image and compression enabled
        compressed = False
        final_filename = original_filename
        
        if compress and file_type == 'image':
            file_data, final_filename = compress_image(file_data, original_filename)
            compressed = True
        
        # Save file
        relative_path = save_file(file_data, final_filename, subfolder)
        
        return {
            'success': True,
            'filename': final_filename,
            'original_filename': original_filename,
            'path': relative_path,
            'size': len(file_data),
            'original_size': file_size,
            'type': file_type,
            'compressed': compressed,
            'message': 'File uploaded successfully'
        }
    
    except Exception as e:
        logger.error(f"[Upload] Error processing upload: {e}")
        return {
            'success': False,
            'message': f'Upload failed: {str(e)}'
        }


def delete_file(file_path):
    """Delete uploaded file"""
    try:
        full_path = os.path.join(UPLOAD_FOLDER, file_path)
        if os.path.exists(full_path):
            os.remove(full_path)
            logger.info(f"[Upload] Deleted file: {full_path}")
            return True
        return False
    except Exception as e:
        logger.error(f"[Upload] Error deleting file: {e}")
        return False


def get_upload_stats():
    """Get upload folder statistics"""
    try:
        total_size = 0
        file_count = 0
        
        for root, dirs, files in os.walk(UPLOAD_FOLDER):
            for file in files:
                file_path = os.path.join(root, file)
                total_size += os.path.getsize(file_path)
                file_count += 1
        
        return {
            'total_files': file_count,
            'total_size': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'upload_folder': UPLOAD_FOLDER
        }
    except Exception as e:
        logger.error(f"[Upload] Error getting stats: {e}")
        return None
