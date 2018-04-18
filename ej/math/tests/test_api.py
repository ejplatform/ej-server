from django.urls import reverse
from rest_framework import status

from ej.math.models import Job
from ej_conversations.mommy_recipes import *

pytestmark = pytest.mark.django_db

@pytest.mark.skip('breakage due to change to conversations-app')
class TestJobAPI:

    def update_url(self, job):
        return reverse('job-detail', args=(job.id,))

    def delete_url(self, job):
        return reverse('job-detail', args=(job.id,))

    def create_read_url(self):
        return reverse('job-list')

    def test_get_list_without_login_should_return_200(self, client):
        response = client.get(self.create_read_url())
        assert response.status_code == status.HTTP_200_OK

    def test_get_list_logged_in_should_return_200(self, client, user_db):
        client.force_login(user_db)
        response = client.get(self.create_read_url())
        assert response.status_code == status.HTTP_200_OK

    def test_get_list_should_contains_this_cluster_job(self, client, user_db, cluster_job):
        client.force_login(user_db)
        response = client.get(self.create_read_url())
        assert Job.CLUSTERS in str(response.content)

    def test_user_cannot_create_jobs(self, client, user_db, conversation):
        """
        Ensure we can't create a new job object through request.
        """
        client.force_login(user_db)
        last_jobs_count = Job.objects.count()

        data = {
            "conversation": conversation.id,
            "type": Job.CLUSTERS,
        }

        response = client.post(self.create_read_url(), data, format='json')

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert Job.objects.count() == last_jobs_count

    def test_user_cannot_update_jobs(self, client, user_db, cluster_job):
        """
        Ensure we can't update a job object through request.
        """
        client.force_login(user_db)
        data = {
            "status": Job.FAILED,
        }
        update_response = client.patch(
            self.update_url(cluster_job), data,
            content_type='application/json'
        )

        assert update_response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_user_cannot_delete_jobs(self, client, user_db, cluster_job):
        """
        Ensure we can't delete a job object through request.
        """
        client.force_login(user_db)
        last_jobs_counter = Job.objects.count()

        response = client.delete(self.delete_url(cluster_job))

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert Job.objects.count() == last_jobs_counter
