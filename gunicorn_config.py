# Gunicorn configuration file
import multiprocessing

# Bind to 0.0.0.0:8000
bind = '0.0.0.0:8000'

# Number of worker processes
# A good rule of thumb is (2 x number of CPUs) + 1
workers = multiprocessing.cpu_count() * 2 + 1

# Worker class - use gevent for better performance
worker_class = 'gevent'

# Maximum number of simultaneous clients
worker_connections = 1000

# Maximum number of requests a worker will process before restarting
max_requests = 1000
max_requests_jitter = 50

# Timeout for worker processes in seconds
timeout = 30

# Restart workers that have taken more than 30 seconds to respond
graceful_timeout = 30

# Restart workers after this many seconds
keepalive = 2

# Log settings
logfile = 'logs/gunicorn.log'
loglevel = 'info'
accesslog = 'logs/access.log'
errorlog = 'logs/error.log'
access_log_format = '%({X-Forwarded-For}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process name
proc_name = 'fems_gunicorn'

# Django settings module
raw_env = ['DJANGO_SETTINGS_MODULE=fems.settings_prod']

# Preload application code before worker processes are forked
preload_app = True

# Daemonize the Gunicorn process (run in background)
daemon = False