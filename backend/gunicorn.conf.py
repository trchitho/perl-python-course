"""
Gunicorn Configuration for Production
Optimized for high availability and performance
"""
import os
import multiprocessing

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"
backlog = 2048

# Worker processes
workers = int(os.getenv('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'sync'  # or 'gevent' for async
worker_connections = 1000
max_requests = 1000  # Restart workers after N requests (prevents memory leaks)
max_requests_jitter = 50  # Add randomness to prevent all workers restarting at once
timeout = 30  # Worker timeout
keepalive = 5  # Keep-alive connections

# Logging
accesslog = '-'  # Log to stdout
errorlog = '-'   # Log to stderr
loglevel = os.getenv('LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'elearning-backend'

# Server mechanics
daemon = False  # Don't daemonize (for Docker/systemd)
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Graceful shutdown
graceful_timeout = 30  # Time to wait for workers to finish

# Pre/Post fork hooks
def on_starting(server):
    """Called just before the master process is initialized"""
    server.log.info("=" * 60)
    server.log.info("Starting E-Learning Platform Backend")
    server.log.info(f"Workers: {workers}")
    server.log.info(f"Bind: {bind}")
    server.log.info("=" * 60)

def on_reload(server):
    """Called to recycle workers during a reload"""
    server.log.info("Reloading workers...")

def when_ready(server):
    """Called just after the server is started"""
    server.log.info("Server is ready. Spawning workers...")

def pre_fork(server, worker):
    """Called just before a worker is forked"""
    pass

def post_fork(server, worker):
    """Called just after a worker has been forked"""
    server.log.info(f"Worker spawned (pid: {worker.pid})")

def pre_exec(server):
    """Called just before a new master process is forked"""
    server.log.info("Forked child, re-executing.")

def worker_int(worker):
    """Called when a worker receives the SIGINT or SIGQUIT signal"""
    worker.log.info(f"Worker received INT or QUIT signal (pid: {worker.pid})")

def worker_abort(worker):
    """Called when a worker receives the SIGABRT signal"""
    worker.log.info(f"Worker received SIGABRT signal (pid: {worker.pid})")

def on_exit(server):
    """Called just before exiting Gunicorn"""
    server.log.info("Shutting down E-Learning Platform Backend")
