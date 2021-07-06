web: gunicorn --timeout 300 wsgi -w 8 -b :$PORT --access-logfile - --error-logfile - --access-logformat '[%(h)s] %({request_id}i)s %(u)s %(t)s "%(r)s" %(s)s %(D)s %(b)s "%(f)s" "%(a)s"'
dworker: celery -A blueapps.core.celery worker -Q default -n default@%h -c 5 -l info --maxtasksperchild=50
pworker: celery -A blueapps.core.celery worker -Q pipeline,pipeline_priority -n pipeline_worker@%h -c 5 -l info --maxtasksperchild=50
sworker: celery -A blueapps.core.celery worker -A blueapps.core.celery -Q service_schedule,service_schedule_priority -c 5 -l info -n schedule_worker@%h --maxtasksperchild=50
cworker: celery -A blueapps.core.celery worker -Q pipeline_additional_task,pipeline_additional_task_priority -n common_worker@%h -c 5 -l info --maxtasksperchild=50
erworker: celery -A blueapps.core.celery worker -Q er_execute,er_schedule -n ri_worker@%h -l info -c 10 -l info --maxtasksperchild=50
beat: celery -A blueapps.core.celery beat -l info
pwatch: python manage.py watch_process
