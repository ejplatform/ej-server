from django.db import models
from model_utils import Choices
from model_utils.fields import StatusField

from boogie import rules
from boogie.rest import rest_api

@rest_api()
class Candidate(models.Model):

    """A political candidate. """

    CANDIDACY_OPTIONS = Choices('senadora')
    PARTY_OPTIONS = Choices('pt', 'psdb')

    name = models.CharField(max_length=100,
                            help_text="The name of the candidate")
    candidacy = StatusField(choices_name='CANDIDACY_OPTIONS',
                            help_text="the candadite candidacy")
    urn = models.IntegerField(help_text="The candidate urn number")
    party = StatusField(choices_name='PARTY_OPTIONS',
                        help_text="The candidate party initials")
    image = models.FileField(upload_to="candidates", default="default.jpg")
