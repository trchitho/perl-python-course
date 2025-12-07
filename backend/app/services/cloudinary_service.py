"""
Cloudinary Upload Service
Upload videos and images to Cloudinary
"""
import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
import logging
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)

# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME', '')
CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY', '')
CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET', '')

# Check if Cloudinary is configured
CLOUDINARY_ENABLED = all([CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET])

if CLOUDINARY_ENABLED:
    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET,
        secure=True
    )
    logger.info("[Cloudinary] Service initialized")
else:
    logger.warning("[Cloudinary] Not configured - using local storage")


def is_enabled():
    """Check if Cloudinary is enabled"""
    return CLOUDINARY_ENABLED


def upload_video(file_data, original_filename, folder='elearning/videos'):
    """
    Upload video to Cloudinary
    
    Args:
        file_data: File bytes or file path
        original_filename: Original filename
        folder: Cloudinary folder (default: elearning/videos)
    
    Returns:
        dict: {
            'success': bool,
            'url': str,  # Cloudinary URL
            'secure_url': str,  # HTTPS URL
            'public_id': str,  # Cloudinary public ID
            'resource_type': str,
            'format': str,
            'duration': float,  # Video duration in seconds
            'size': int,
            'message': str
        }
    """
    if not CLOUDINARY_ENABLED:
        return {
            'success': False,
            'message': 'Cloudinary not configured'
        }
    
    try:
        # Get filename without extension for public_id
        filename = os.path.splitext(secure_filename(original_filename))[0]
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            file_data,
            resource_type='video',
            folder=folder,
            public_id=filename,
            overwrite=True,  # Allow overwriting existing files
            unique_filename=False,  # Use exact filename
            invalidate=True,  # Invalidate CDN cache
            # Video optimization
            eager=[
                {'streaming_profile': 'hd', 'format': 'm3u8'},  # HLS streaming
                {'width': 1280, 'height': 720, 'crop': 'limit', 'format': 'mp4'}  # HD version
            ],
            eager_async=True,  # Process in background
        )
        
        logger.info(f"[Cloudinary] Uploaded video: {result['public_id']}")
        
        return {
            'success': True,
            'url': result['url'],
            'secure_url': result['secure_url'],
            'public_id': result['public_id'],
            'resource_type': result['resource_type'],
            'format': result.get('format', ''),
            'duration': result.get('duration', 0),
            'size': result.get('bytes', 0),
            'width': result.get('width', 0),
            'height': result.get('height', 0),
            'message': 'Video uploaded successfully to Cloudinary'
        }
    
    except Exception as e:
        logger.error(f"[Cloudinary] Upload failed: {e}")
        return {
            'success': False,
            'message': f'Upload failed: {str(e)}'
        }


def upload_image(file_data, original_filename, folder='elearning/images'):
    """
    Upload image to Cloudinary with optimization
    
    Args:
        file_data: File bytes or file path
        original_filename: Original filename
        folder: Cloudinary folder
    
    Returns:
        dict: Upload result
    """
    if not CLOUDINARY_ENABLED:
        return {
            'success': False,
            'message': 'Cloudinary not configured'
        }
    
    try:
        filename = os.path.splitext(secure_filename(original_filename))[0]
        
        result = cloudinary.uploader.upload(
            file_data,
            resource_type='image',
            folder=folder,
            public_id=filename,
            overwrite=True,  # Allow overwriting existing files
            unique_filename=False,  # Use exact filename
            invalidate=True,  # Invalidate CDN cache
            # Image optimization
            transformation=[
                {'quality': 'auto', 'fetch_format': 'auto'}
            ]
        )
        
        logger.info(f"[Cloudinary] Uploaded image: {result['public_id']}")
        
        return {
            'success': True,
            'url': result['url'],
            'secure_url': result['secure_url'],
            'public_id': result['public_id'],
            'resource_type': result['resource_type'],
            'format': result.get('format', ''),
            'size': result.get('bytes', 0),
            'width': result.get('width', 0),
            'height': result.get('height', 0),
            'message': 'Image uploaded successfully to Cloudinary'
        }
    
    except Exception as e:
        logger.error(f"[Cloudinary] Image upload failed: {e}")
        return {
            'success': False,
            'message': f'Upload failed: {str(e)}'
        }


def upload_document(file_data, original_filename, folder='elearning/documents'):
    """
    Upload document (PDF, Word, etc.) to Cloudinary
    
    Args:
        file_data: File bytes or file path
        original_filename: Original filename
        folder: Cloudinary folder
    
    Returns:
        dict: Upload result
    """
    if not CLOUDINARY_ENABLED:
        return {
            'success': False,
            'message': 'Cloudinary not configured'
        }
    
    try:
        filename = secure_filename(original_filename)
        
        result = cloudinary.uploader.upload(
            file_data,
            resource_type='raw',  # For non-image/video files
            folder=folder,
            public_id=filename,
            overwrite=True,  # Allow overwriting existing files
            unique_filename=False,  # Use exact filename, don't add random suffix
            invalidate=True  # Invalidate CDN cache to get fresh content
        )
        
        logger.info(f"[Cloudinary] Uploaded document: {result['public_id']}")
        
        return {
            'success': True,
            'url': result['url'],
            'secure_url': result['secure_url'],
            'public_id': result['public_id'],
            'resource_type': result['resource_type'],
            'format': result.get('format', ''),
            'size': result.get('bytes', 0),
            'message': 'Document uploaded successfully to Cloudinary'
        }
    
    except Exception as e:
        logger.error(f"[Cloudinary] Document upload failed: {e}")
        return {
            'success': False,
            'message': f'Upload failed: {str(e)}'
        }


def delete_file(public_id, resource_type='video'):
    """
    Delete file from Cloudinary
    
    Args:
        public_id: Cloudinary public ID
        resource_type: 'video', 'image', or 'raw'
    
    Returns:
        bool: Success status
    """
    if not CLOUDINARY_ENABLED:
        return False
    
    try:
        result = cloudinary.uploader.destroy(public_id, resource_type=resource_type)
        logger.info(f"[Cloudinary] Deleted: {public_id}")
        return result.get('result') == 'ok'
    except Exception as e:
        logger.error(f"[Cloudinary] Delete failed: {e}")
        return False


def get_video_url(public_id, transformation=None):
    """
    Get optimized video URL
    
    Args:
        public_id: Cloudinary public ID
        transformation: Optional transformation dict
    
    Returns:
        str: Video URL
    """
    if not CLOUDINARY_ENABLED:
        return None
    
    try:
        url = cloudinary.CloudinaryVideo(public_id).build_url(transformation=transformation)
        return url
    except Exception as e:
        logger.error(f"[Cloudinary] Get URL failed: {e}")
        return None


def get_storage_stats():
    """Get Cloudinary usage statistics"""
    if not CLOUDINARY_ENABLED:
        return {
            'enabled': False,
            'message': 'Cloudinary not configured'
        }
    
    try:
        usage = cloudinary.api.usage()
        
        return {
            'enabled': True,
            'cloud_name': CLOUDINARY_CLOUD_NAME,
            'plan': usage.get('plan', 'free'),
            'credits': {
                'used': usage.get('credits', {}).get('usage', 0),
                'limit': usage.get('credits', {}).get('limit', 0),
            },
            'bandwidth': {
                'used': usage.get('bandwidth', {}).get('usage', 0),
                'limit': usage.get('bandwidth', {}).get('limit', 0),
                'used_mb': round(usage.get('bandwidth', {}).get('usage', 0) / (1024 * 1024), 2),
            },
            'storage': {
                'used': usage.get('storage', {}).get('usage', 0),
                'limit': usage.get('storage', {}).get('limit', 0),
                'used_mb': round(usage.get('storage', {}).get('usage', 0) / (1024 * 1024), 2),
            },
            'transformations': {
                'used': usage.get('transformations', {}).get('usage', 0),
                'limit': usage.get('transformations', {}).get('limit', 0),
            }
        }
    except Exception as e:
        logger.error(f"[Cloudinary] Stats failed: {e}")
        return {
            'enabled': True,
            'error': str(e)
        }
