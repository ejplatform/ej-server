from functools import wraps

from celery import shared_task
from pushtogether_math import cluster

from ej_conversations.models import Conversation
from .models import Job


# decorator to avoid code duplication
def update_job(fn):
    """
    Decorator that will update Job with result of the function
    """

    # wraps will make the name and docstring of fn available for introspection
    @wraps(fn)
    def wrapper(job_id, *args, **kwargs):
        job = Job.objects.get(pk=job_id)
        job.status = Job.STARTED
        job.save()
        try:
            # execute the function fn
            result = fn(*args, **kwargs)
            job.result = result
            job.status = Job.FINISHED if result else Job.STUCK
            job.save()
        except:
            job.result = None
            job.status = Job.FAILED
        job.save()

    return wrapper


@shared_task
@update_job
def get_clusters(conversation_id):
    """
    Celery task that receives an conversation ID, checks if this conversation
    has sufficient data to be clustered, than returns the clusters if it's ok,
    or None if it isn't.
    """
    conversation = Conversation.objects.get(pk=conversation_id)
    if has_sufficient_data(conversation):
        votes = conversation.get_vote_data()
        return cluster.get_clusters(votes, range(2, 5))


def has_sufficient_data(conversation):
    """
    Check if the conversation available data respect the limits of the
    math configuration variables.
    """
    if (conversation.total_participants < Job.MATH_MIN_USERS or
        conversation.total_comments < Job.MATH_MIN_COMMENTS or
        conversation.total_votes < Job.MATH_MIN_VOTES):
        return False
    return True


TASK_MAPPING = {
    'CLUSTERS': get_clusters,
}
