web: gunicorn --timeout 600 --max-requests 500 --max-requests-jitter 100 wsgi -w 8 -b :$PORT --access-logfile - --error-logfile - --access-logformat '[%(h)s] %({request_id}i)s %(u)s %(t)s "%(r)s" %(s)s %(D)s %(b)s "%(f)s" "%(a)s"'
dworker: celery -A blueapps.core.celery worker -Q default -n default@%h -c 5 -l info --maxtasksperchild=50
cworker: celery -A blueapps.core.celery worker -Q pipeline_additional_task,pipeline_additional_task_priority -n common_worker@%h -c 5 -l info --maxtasksperchild=50
ereworker: celery -A blueapps.core.celery worker -Q er_execute -n ri_worker@%h -l info -c 10 -l info --maxtasksperchild=100
ersworker: celery -A blueapps.core.celery worker -Q er_schedule -n ri_worker@%h -l info -c 10 -l info --maxtasksperchild=200
beat: celery -A blueapps.core.celery beat -l info
pwatch: python manage.py watch_process
