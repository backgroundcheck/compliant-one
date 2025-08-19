import multiprocessing
import os

bind = f"0.0.0.0:{int(os.getenv('API_PORT', '8000'))}"
workers = int(os.getenv("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
worker_class = "uvicorn.workers.UvicornWorker"
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info").lower()
keepalive = 30
threads = int(os.getenv("GUNICORN_THREADS", "1"))

# Timeouts
timeout = int(os.getenv("GUNICORN_TIMEOUT", "120"))
