import pytest
import time

from pushtogether.conversations.tests import helpers as cv_helpers
from pushtogether.math.models import Job
from . import helpers


pytestmark = pytest.mark.django_db


class TestClusterJob:

    def test_create_valid_cluster_job(self, conversation):
        old_counter = Job.objects.filter(type=Job.CLUSTERS).count()
        helpers.create_valid_job(conversation)
        new_counter = Job.objects.filter(type=Job.CLUSTERS).count()

        assert old_counter == 0
        assert new_counter == 1

    def test_jobs_should_stuck_without_sufficient_users(self, conversation):
        """
        Jobs can't be created if there are less than 5 participants
        """
        users_list = cv_helpers.create_valid_users(4)
        cv_helpers.populate_conversation_comments(conversation, users_list, n_comments_per_user=2)
        cv_helpers.populate_conversation_votes(conversation, users_list, max_votes_per_user=3)
        job = helpers.create_valid_job(conversation)

        assert job.status == Job.STUCKED

    def test_jobs_cannot_be_created_without_sufficient_comments(self, user, conversation):
        """
        Jobs can't be created if there are less than 5 comments
        """
        users_list = cv_helpers.create_valid_users(5)
        cv_helpers.create_valid_comments(4, conversation, user)
        cv_helpers.populate_conversation_votes(conversation, users_list, max_votes_per_user=1)
        job = helpers.create_valid_job(conversation)

        assert job.status == Job.STUCKED

    def test_jobs_cannot_be_created_without_sufficient_votes(self, user, conversation):
        """
        Jobs can't be created if there are less than 5 votes
        """
        users_list = cv_helpers.create_valid_users(5)
        comments = cv_helpers.create_valid_comments(5, conversation, user)
        cv_helpers.create_valid_vote(comments[0], users_list[0])
        job = helpers.create_valid_job(conversation)

        assert job.status == Job.STUCKED

    def test_jobs_can_be_created_with_sufficient_users_and_comments(self, user, conversation):
        """
        Jobs can be created if there are sufficient resources
        """
        users_list = cv_helpers.create_valid_users(5)
        cv_helpers.create_valid_comments(5, conversation, user)
        cv_helpers.populate_conversation_votes(conversation, users_list, max_votes_per_user=1)
        job = helpers.create_valid_job(conversation)

        assert job.status == Job.FINISHED

    def test_jobs_cannot_be_created_if_there_is_a_pending_job(self, conversation):
        """
        Jobs can't be created if the same conversation has a pending job
        """
        pass
