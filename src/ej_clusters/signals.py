from django.db.models.signals import post_save
from django.dispatch import receiver

from ej_conversations.models import Vote
from . import tasks


@receiver(post_save, sender=Vote)
def on_user_vote(sender, instance, created, **kwargs):
    """
    Trigger a cluster update when user vote.
    """
    if created:
        vote = instance
        comment = vote.comment
        conversation = comment.conversation
        clusterization = conversation.get_clusterization(None)

        if clusterization is not None:
            clusterization.pending_votes.add(vote)
            clusterization.pending_comments.add(comment)
            tasks.update_clusterization.send(clusterization.id)
