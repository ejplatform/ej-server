from pushtogether_math import cluster
from functools import wraps
from celery import shared_task

from .models import Job
from .celeryconf import app


# decorator to avoid code duplication
def update_job(fn):  
    """Decorator that will update Job with result of the function"""

    # wraps will make the name and docstring of fn available for introspection
    @wraps(fn)
    def wrapper(job_id, *args, **kwargs):
        job = Job.objects.get(id=job_id)
        job.status = Job.STATUS.STARTED
        job.save()
        try:
            # execute the function fn
            result = fn(*args, **kwargs)
            job.result = result
            job.status = Job.STATUS.FINISHED
            job.save()
        except:
            job.result = None
            job.status = Job.STATUS.FAILED
        job.save()
    return wrapper


#@app.task
#@update_job
@shared_task
def get_clusters(votes):
    return cluster.get_clusters(votes)

TASK_MAPPING = {  
    'CLUSTERS': get_clusters,
}
