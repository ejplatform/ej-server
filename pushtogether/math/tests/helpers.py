import pytest

from pushtogether.math.models import Job


pytestmark = pytest.mark.django_db


def create_valid_job(conversation, type=Job.CLUSTERS):
    job = Job.objects.create(
        type=type,
        conversation=conversation
    )
    job.save()
    return job
