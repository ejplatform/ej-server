from actstream import action
from django.db.models import Count
from django.db.models.signals import post_save
from actstream import action
from ej.conversations.models import Comment, Conversation, Vote
from ej.users.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.translation import ugettext as _
from pinax.badges.registry import badges
from pinax.points.models import award_points

from ej.conversations.models import Comment, Conversation, Vote
from ej.users.models import User


def actions_when_comment_saved(instance):
    action.send(instance.author,
                verb='created comment',
                description=_('Created Comment'),
                action_object=instance,
                target=instance.conversation,
                timestamp=instance.created_at)
    if instance.approval == Comment.APPROVED:
        award_points(instance.author, 'comment_approved', reason="Comment Approved", source=instance)
        action.send(instance.author,
                    verb='had comment approved',
                    description=_('Had Comment Approved'),
                    action_object=instance,
                    target=instance.conversation)


def actions_when_vote_created(instance):
    award_points(instance.author, 'voted', reason="Voted on Conversation", source=instance)

    if instance.value == Vote.AGREE:
        action.send(instance.author,
                    verb='agreed with',
                    description=_('Agreed With'),
                    action_object=instance,
                    target=instance.comment,
                    timestamp=instance.created_at)

    if instance.value == Vote.PASS:
        action.send(instance.author,
                    verb='passed on',
                    description=_('Passed On'),
                    action_object=instance,
                    target=instance.comment,
                    timestamp=instance.created_at)

    if instance.value == Vote.DISAGREE:
        action.send(instance.author,
                    verb='disagreed with',
                    description=_('Disagreed With'),
                    action_object=instance,
                    target=instance.comment,
                    timestamp=instance.created_at)

    # Let's find out whether vote is in a new conversation
    conversations = (
        Conversation.objects
            .filter(comments__votes__author=instance.author,
                    comments__votes__created_at__lte=instance.created_at)
            .distinct()
            .annotate(number_of_votes=Count('comments__votes'))
    )
    number_of_first_votes = sum([x.number_of_votes for x in conversations if x.number_of_votes == 1])
    if len(conversations) == 2 and number_of_first_votes >= 1:
        award_points(instance.author, 'voted_first_time_in_second_conversation',
                     reason='Voted first time in second conversation', source=instance)
    if len(conversations) > 2 and number_of_first_votes >= 1:
        award_points(instance.author, 'voted_first_time_in_new_conversation_after_second',
                     reason='Voted first time in new conversation', source=instance)

    # And finally, the badges
    badges.possibly_award_badge('vote_cast', user=instance.author)


def actions_when_conversation_created(instance):
    action.send(instance.author,
                verb='created conversation',
                description=_('Created Conversation'),
                action_object=instance,
                timestamp=instance.created_at)


def actions_when_user_created(instance):
    action.send(instance,
                verb='user created',
                description=_('Was Created'),
                action_object=instance,
                target=instance,
                timestamp=instance.date_joined)
    badges.possibly_award_badge("user_created", user=instance)
    award_points(instance, 'user_created', reason="User Created")


def actions_when_user_profile_filled(instance):
    action.send(instance,
                verb='filled profile',
                description=_('Filled Profile'),
                action_object=instance,
                target=instance)
    badges.possibly_award_badge("user_profile_filled", user=instance)
    award_points(instance, 'user_profile_filled')


@receiver(post_save, sender=Comment)
def helper_comment_function(sender, instance, created, **kwargs):
    actions_when_comment_saved(instance)


@receiver(post_save, sender=Vote)
def vote_cast(sender, instance, created, **kwargs):
    if created:
        actions_when_vote_created(instance)


@receiver(post_save, sender=Conversation)
def conversation_saved(sender, instance, created, **kwargs):
    if created:
        actions_when_conversation_created(instance)


@receiver(post_save, sender=User)
def user_created(sender, instance, created, **kwargs):
    if created:
        actions_when_user_created(instance)


@receiver(post_save, sender=User)
def user_profile_filled(sender, instance, created, **kwargs):
    if instance.profile_filled:
        actions_when_user_profile_filled(instance)
