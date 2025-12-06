"""
WSGI Entry Point for Production Deployment
Uses Gunicorn for production-grade serving
"""
import os
import logging
from app import create_app
from app.middleware.shutdown_handler import init_shutdown_handler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)

# Create Flask application
app = create_app()

# Initialize graceful shutdown
init_shutdown_handler(app)

# Log startup
with app.app_context():
    logging.info("=" * 60)
    logging.info("E-Learning Platform - Production Mode")
    logging.info("=" * 60)
    logging.info(f"Environment: {os.getenv('FLASK_ENV', 'production')}")
    logging.info(f"Debug: {app.config.get('DEBUG', False)}")
    logging.info("=" * 60)

if __name__ == "__main__":
    # This is only used for development
    # In production, use: gunicorn wsgi:app
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
