from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from pushtogether.conversations.models import Comment, Conversation, Vote
from django.contrib.contenttypes.fields import ContentType
from actstream.models import Action
from pushtogether.gamification.signals import actions_when_vote_created, \
    actions_when_user_created, actions_when_comment_saved, \
    actions_when_user_profile_filled, actions_when_conversation_created


class Command(BaseCommand):
    help = 'Create Scores, points and badges for your app'

    def handle(self, *args, **options):

        vote_type = ContentType.objects.get_for_model(Vote)
        for vote in Vote.objects.all():
            if not Action.objects.filter(action_object_content_type_id=vote_type.id, action_object_object_id=vote.id):
                print('entrou no if not')
                actions_when_vote_created(vote)

        conversation_type = ContentType.objects.get_for_model(Conversation)
        for conversation in Conversation.objects.all():
            if not Action.objects.filter(action_object_content_type_id=conversation_type.id,
                                         action_object_object_id=conversation.id, verb='created conversation'):
                actions_when_conversation_created(conversation)

        comment_type = ContentType.objects.get_for_model(Comment)
        for comment in Comment.objects.all():
            if not Action.objects.filter(action_object_content_type_id=comment_type.id,
                                         action_object_object_id=comment.id):
                actions_when_comment_saved(comment)

        user_type = ContentType.objects.get_for_model(get_user_model())
        for user in get_user_model().objects.all():
            if not Action.objects.filter(action_object_content_type_id=user_type.id,
                                         action_object_object_id=user.id, verb='user created'):
                actions_when_user_created(user)
                if user.profile_filled:
                    actions_when_user_profile_filled(user)
