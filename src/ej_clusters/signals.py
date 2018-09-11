from django.db.models.signals import post_save
from django.dispatch import receiver

from ej_conversations.models import Vote, Conversation
from . import models

log = models.log


@receiver(post_save, sender=Vote)
def on_user_vote(sender, instance, created, **kwargs):
    """
    Trigger a cluster update when user vote.
    """
    if created:
        vote = instance
        log.info(vote)

        comment = vote.comment
        conversation = comment.conversation
        clusterization = models.get_clusterization(conversation)

        if comment.votes.count() == 5:
            clusterization.unprocessed_comments += 1
        if vote.author.has_perm('ej.can_be_clusterized', conversation):
            clusterization.unprocessed_votes += 1
        clusterization.update()


@receiver(post_save, sender=Conversation)
def on_conversation(sender, instance, created, **kwargs):
    """
    Save one clusterization object per conversation.s
    """
    if created:
        models.Clusterization.objects.create(conversation=instance)
