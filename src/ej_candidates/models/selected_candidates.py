from django.db import models
from ej_users.models import User
from .candidate import Candidate
from django.db.models.signals import post_save
from django.dispatch import receiver

from boogie import rules
from boogie.rest import rest_api

@rest_api()
class SelectedCandidate(models.Model):

    """Candidates selected by a user"""
    def __str__(self):
        return "%s - %s" % (self.candidate.name, self.candidate.party)

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, null=True)

@receiver(post_save, sender=SelectedCandidate)
def notify_user(sender, instance, created, **kwargs):
    pass