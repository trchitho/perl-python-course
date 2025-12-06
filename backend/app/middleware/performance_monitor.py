"""
Performance Monitoring Middleware (QA02)
Tracks response times and request metrics
"""
import time
from flask import request, g
import logging
import sys

# Configure logger to output to console
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Add console handler if not already present
if not logger.handlers:
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s:%(name)s: %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

class PerformanceMetrics:
    """Simple performance metrics tracker"""
    
    def __init__(self):
        self.requests = []
        self.max_stored = 1000  # Keep last 1000 requests
    
    def record_request(self, endpoint, method, duration, status_code):
        """Record a request"""
        self.requests.append({
            'endpoint': endpoint,
            'method': method,
            'duration': duration,
            'status_code': status_code,
            'timestamp': time.time()
        })
        
        # Keep only recent requests
        if len(self.requests) > self.max_stored:
            self.requests = self.requests[-self.max_stored:]
    
    def get_stats(self, endpoint=None):
        """Get statistics"""
        if endpoint:
            filtered = [r for r in self.requests if r['endpoint'] == endpoint]
        else:
            filtered = self.requests
        
        if not filtered:
            return {
                'count': 0,
                'avg_duration': 0,
                'min_duration': 0,
                'max_duration': 0
            }
        
        durations = [r['duration'] for r in filtered]
        return {
            'count': len(filtered),
            'avg_duration': sum(durations) / len(durations),
            'min_duration': min(durations),
            'max_duration': max(durations),
            'recent_requests': filtered[-10:]  # Last 10 requests
        }

# Global metrics instance
metrics = PerformanceMetrics()

def performance_monitor_middleware(app):
    """Add performance monitoring to Flask app"""
    
    @app.before_request
    def before_request():
        """Record request start time"""
        g.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        """Record request completion and metrics"""
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            
            # Record metrics
            metrics.record_request(
                endpoint=request.endpoint or 'unknown',
                method=request.method,
                duration=duration,
                status_code=response.status_code
            )
            
            # Log all requests with performance info (QA02: Performance monitoring)
            status_icon = "✅" if response.status_code < 400 else "❌"
            logger.info(
                f"{status_icon} {request.method} {request.path} - "
                f"{duration:.3f}s - Status: {response.status_code}"
            )
            
            # Log slow requests with warning (QA02: Performance monitoring)
            if duration > 5.0:  # Slower than 5 seconds
                logger.warning(
                    f"⚠️  SLOW REQUEST: {request.method} {request.path} "
                    f"took {duration:.2f}s (status: {response.status_code})"
                )
            
            # Add performance header
            response.headers['X-Response-Time'] = f"{duration:.3f}s"
        
        return response
    
    return app
