"""
Graceful Shutdown Handler
Ensures clean shutdown of connections and resources
"""
import signal
import sys
import logging
from flask import current_app

logger = logging.getLogger(__name__)

shutdown_in_progress = False


def graceful_shutdown(signum, frame):
    """Handle shutdown signals gracefully"""
    global shutdown_in_progress
    
    if shutdown_in_progress:
        logger.warning("[Shutdown] Already shutting down, forcing exit...")
        sys.exit(1)
    
    shutdown_in_progress = True
    
    logger.info(f"[Shutdown] Received signal {signum}, initiating graceful shutdown...")
    
    try:
        # Close database connections
        from app import db
        logger.info("[Shutdown] Closing database connections...")
        db.session.remove()
        db.engine.dispose()
        logger.info("[Shutdown] Database connections closed")
        
        # Close Redis connections
        try:
            from app.services.cache_service import get_redis
            redis_client = get_redis()
            if redis_client:
                logger.info("[Shutdown] Closing Redis connections...")
                redis_client.close()
                logger.info("[Shutdown] Redis connections closed")
        except Exception as e:
            logger.warning(f"[Shutdown] Redis cleanup error: {e}")
        
        logger.info("[Shutdown] Graceful shutdown complete")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"[Shutdown] Error during shutdown: {e}")
        sys.exit(1)


def register_shutdown_handlers():
    """Register signal handlers for graceful shutdown"""
    # Handle SIGTERM (sent by Docker, K8s, systemd)
    signal.signal(signal.SIGTERM, graceful_shutdown)
    
    # Handle SIGINT (Ctrl+C)
    signal.signal(signal.SIGINT, graceful_shutdown)
    
    logger.info("[Shutdown] Graceful shutdown handlers registered")


def init_shutdown_handler(app):
    """Initialize shutdown handler for Flask app"""
    with app.app_context():
        register_shutdown_handlers()
