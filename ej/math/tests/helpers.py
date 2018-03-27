import pytest

from ej.math.models import Job


def create_valid_job(conversation, type=Job.CLUSTERS):
    job = Job(
        type=type,
        conversation=conversation
    )
    job.save(delay=False)
    return Job.objects.get(pk=job.id)
