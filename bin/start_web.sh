python manage.py collectstatic --noinput
gunicorn --timeout 600 --max-requests 200 --max-requests-jitter 20 wsgi -w 8 -b :$PORT --access-logfile - --error-logfile - --access-logformat '[%(h)s] %({request_id}i)s %(u)s %(t)s "%(r)s" %(s)s %(D)s %(b)s "%(f)s" "%(a)s"'
