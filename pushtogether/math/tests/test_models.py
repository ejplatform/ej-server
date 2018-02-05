import pytest
import time

from pushtogether.math.models import Job
from .helpers import create_valid_job


pytestmark = pytest.mark.django_db


class TestClusterJob:

    def test_create_valid_cluster_job(self, conversation):
        old_counter = Job.objects.filter(type=Job.CLUSTERS).count()
        create_valid_job(conversation)
        new_counter = Job.objects.filter(type=Job.CLUSTERS).count()

        assert old_counter == 0
        assert new_counter == 1

    def test_cluster_job_should_start_as_pending_job(self, cluster_job):
        assert cluster_job.status == Job.PENDING
