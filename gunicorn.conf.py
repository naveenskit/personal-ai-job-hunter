import multiprocessing

workers = multiprocessing.cpu_count() * 2 + 1
bind = "0.0.0.0:8000"
timeout = 30
keepalive = 2
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Recommended for graceful timeouts in workers
graceful_timeout = 30
