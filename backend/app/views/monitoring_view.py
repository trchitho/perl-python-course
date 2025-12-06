"""
Monitoring and Health Check Endpoints (QA02 - Performance)
Provides system health and performance metrics
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from flask_cors import cross_origin
from app.services.jwt_service import require_roles
from app.middleware.performance_monitor import metrics
from app.services.cache_service import get_cache_stats, cache_clear
from app import db
import time

monitoring_bp = Blueprint('monitoring', __name__)

@monitoring_bp.after_request
def add_cors_headers(response):
    """Add CORS headers to all monitoring responses"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    return response

@monitoring_bp.route('/health', methods=['GET', 'OPTIONS'])
@cross_origin()
def health_check():
    """
    Health check endpoint (QA02 - Performance)
    Checks database connectivity and system status
    """
    health_status = {
        'status': 'healthy',
        'timestamp': time.time(),
        'checks': {}
    }
    
    # Check database connection
    try:
        db.session.execute(db.text('SELECT 1'))
        health_status['checks']['database'] = {
            'status': 'healthy',
            'message': 'Database connection OK'
        }
    except Exception as e:
        health_status['status'] = 'unhealthy'
        health_status['checks']['database'] = {
            'status': 'unhealthy',
            'message': f'Database error: {str(e)}'
        }
    
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return jsonify(health_status), status_code

@monitoring_bp.route('/health/live', methods=['GET'])
def liveness_check():
    """Liveness probe - checks if application is running"""
    return jsonify({
        'status': 'alive',
        'timestamp': time.time()
    }), 200

@monitoring_bp.route('/health/ready', methods=['GET'])
def readiness_check():
    """Readiness probe - checks if application is ready"""
    try:
        db.session.execute(db.text('SELECT 1'))
        return jsonify({
            'status': 'ready',
            'timestamp': time.time()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'not_ready',
            'error': str(e),
            'timestamp': time.time()
        }), 503

@monitoring_bp.route('/metrics', methods=['GET'])
@jwt_required()
@require_roles('admin')
def get_metrics():
    """
    Get performance metrics (QA02 - Performance)
    Admin only endpoint
    """
    try:
        overall_stats = metrics.get_stats()
        
        return jsonify({
            'performance': overall_stats,
            'timestamp': time.time()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/cache-stats', methods=['GET'])
def get_cache_stats_public():
    """Get cache statistics (public for demo)"""
    stats = get_cache_stats()
    return jsonify(stats), 200

@monitoring_bp.route('/cache/stats', methods=['GET'])
@jwt_required()
@require_roles('admin')
def get_cache_stats_admin():
    """Get cache statistics (admin)"""
    stats = get_cache_stats()
    return jsonify(stats), 200

@monitoring_bp.route('/cache/clear', methods=['POST'])
@jwt_required()
@require_roles('admin')
def clear_cache_endpoint():
    """Clear all cache (admin only)"""
    success = cache_clear()
    if success:
        return jsonify({'message': 'Cache cleared successfully'}), 200
    return jsonify({'error': 'Failed to clear cache'}), 500
