from django.db import models
from ej_users.models import User
from .candidate import Candidate
from django.db.models.signals import post_save
from django.dispatch import receiver
from ej_messages.models import Message
from ej_channels.models import Channel

from boogie import rules
from boogie.rest import rest_api

@rest_api()
class PressedCandidate(models.Model):

    """Candidates pressed by a user"""
    def __str__(self):
        return "%s - %s" % (self.candidate.name, self.candidate.party)

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, null=True)

@receiver(post_save, sender=PressedCandidate)
def send_message(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        title = instance.candidate.name
        url = instance.candidate.site_url
        try:
            channel = Channel.objects.filter(owner=user, sort="press")[0]
        except IndexError:
            channel = Channel.objects.create(name="press channel", sort="press", owner=user)
            channel.users.add(user)
            channel.save()
        Message.objects.create(channel=channel, title=title, body="")