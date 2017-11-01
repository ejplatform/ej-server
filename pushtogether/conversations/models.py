import re
import datetime
from random import randint
from enum import Enum

from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.db.models import Q
from django.utils.timezone import make_aware, get_current_timezone

from .validators import validate_color

User = get_user_model()


class Conversation(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    title = models.CharField(max_length=255, blank=False)
    description = models.TextField(blank=False)
    polis_id = models.IntegerField(null=True, blank=True)
    dialog = models.TextField(null=True, blank=True)
    response = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    background_image = models.ImageField(
        upload_to='conversations/backgrounds',
        null=True, blank=True)
    background_color = models.CharField(
        max_length=7, validators=[validate_color],
        null=True, blank=True)

    polis_slug = models.CharField(_('Polis slug'), max_length=255, null=True, blank=True)
    polis_url = models.CharField(_('Polis url'), max_length=255, null=True, blank=True)

    # Nudge configuration
    comment_nudge = models.IntegerField(null=True, blank=True) # number of comments
    comment_nudge_interval = models.IntegerField(null=True, blank=True)  # seconds
    comment_nudge_global_limit = models.IntegerField(null=True, blank=True) # number of comments

    class NUDGE(Enum):
        interval_blocked = {
            'state': 'interval_blocked',
            'message': _('Sorry, you are actually blocked. Please wait be able to post again'),
            'status_code': 429,
            'errors': True,
        }
        global_blocked = {
            'state': 'global_blocked',
            'message': _('Sorry, you cannot post more comments in this conversation'),
            'status_code': 429,
            'errors': True,
        }
        eager = {
            'state': 'eager',
            'message': _('Please, be careful posting too many comments'),
            'status_code': 200,
            'errors': False,
        }
        normal = {
            'state': 'normal',
            'message': _('You can still posting comments'),
            'status_code': 200,
            'errors': False,
        }


    def __str__(self):
        return self.title

    @property
    def total_participants(self):
        return User.objects.filter(votes__comment__conversation_id=self.id).distinct().count()

    @property
    def agree_votes(self):
        return Vote.objects.filter(comment__conversation_id=self.id,
                                   value=Vote.AGREE).count()

    @property
    def disagree_votes(self):
        return Vote.objects.filter(comment__conversation_id=self.id,
                                   value=Vote.DISAGREE).count()

    @property
    def pass_votes(self):
        return Vote.objects.filter(comment__conversation_id=self.id,
                                   value=Vote.PASS).count()

    @property
    def total_votes(self):
        return Vote.objects.filter(comment__conversation_id=self.id).count()

    @property
    def approved_comments(self):
        return self.comments.filter(approval=Comment.APPROVED).count()

    @property
    def rejected_comments(self):
        return self.comments.filter(approval=Comment.REJECTED).count()

    @property
    def unmoderated_comments(self):
        return self.comments.filter(approval=Comment.UNMODERATED).count()

    @property
    def total_comments(self):
        return self.comments.count()

    def get_user_participation_ratio(self, user):
        total_approved_comments = self.comments.filter(
            approval=Comment.APPROVED).count()
        user_votes = Vote.objects.filter(
            comment__conversation_id=self.id,
            author=user).count()

        return user_votes/total_approved_comments if total_approved_comments else 0

    def get_random_unvoted_comment(self, user):
        user_unvoted_comments = self.comments.filter(
            ~Q(votes__author_id__exact=user.id),
            approval=Comment.APPROVED)

        pks = user_unvoted_comments.values_list('pk', flat=True)
        comment_counter = len(pks)
        if comment_counter:
            random_idx = randint(0, len(pks))
            while(random_idx == len(pks)):
                random_idx = randint(0, len(pks))
        else:
            raise DoesNotExist(_('There is no comments available for this user'))

        random_comment = user_unvoted_comments.get(pk=pks[random_idx])
        return random_comment

    def get_nudge_status(self, user):
        '''
        Verify specific user nudge status in a conversation
        '''
        if(self._is_user_nudge_global_limit_blocked(user)):
            return self.NUDGE.global_blocked

        user_comments = self._get_nudge_interval_comments(user)
        user_comments_counter = user_comments.count()

        if(self._is_user_nudge_interval_blocked(user_comments_counter)):
            return self.NUDGE.interval_blocked
        elif(self._is_user_nudge_eager(user_comments_counter, user_comments)):
            return self.NUDGE.eager
        else:
            return self.NUDGE.normal
        
    def _is_user_nudge_global_limit_blocked(self, user):
        '''
        Check number of user's comments is lower than the global limit
        '''
        if(self.comment_nudge_global_limit):
            user_comments_counter = user.comments.filter(
                conversation_id=self.id).count()
            return user_comments_counter >= self.comment_nudge_global_limit
        else:
            return False

    def _is_user_nudge_interval_blocked(self, user_comments_counter):
        '''
        User cannot write too many comments. The limit is set by the
        conversation's comment_nudge and comment_nudge_interval
        '''
        if(self.comment_nudge):
            return user_comments_counter >= self.comment_nudge
        else:
            return False

    def _is_user_nudge_eager(self, user_comments_counter, user_comments):
        '''
        A user is an eager user when he creates half of the comments that
        is possible in the middle of the nudge interval
        '''
        if(self.comment_nudge and self.comment_nudge_interval):
            half_nudge = self.comment_nudge//2 - 1
            half_nudge_interval = self.comment_nudge_interval//2
            if(user_comments_counter > half_nudge):
                datetime_limit = self._get_datetime_interval(half_nudge_interval) 
                return user_comments[half_nudge].created_at >= datetime_limit
        return False

    def _get_nudge_interval_comments(self, user):
        '''
        Returns how many comments user has between now and past
        comment_nudge_interval
        '''
        nudge_interval_comments = []
        nudge_interval = self.comment_nudge_interval
        if(nudge_interval):
            datetime_limit = self._get_datetime_interval(nudge_interval)
            nudge_interval_comments = user.comments.filter(
                created_at__gt=datetime_limit,
                conversation_id=self.id)
        return nudge_interval_comments

    def _get_datetime_interval(self, interval):
        timedelta = datetime.timedelta(seconds=interval)
        time_limit = datetime.datetime.now() - timedelta
        return make_aware(time_limit, get_current_timezone())
 

class Comment(models.Model):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    UNMODERATED = "UNMODERATED"

    APPROVEMENT_CHOICES = (
        (APPROVED, _('approved')),
        (REJECTED, _('rejected')),
        (UNMODERATED, _('unmoderated')),
    )

    conversation = models.ForeignKey(Conversation, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='comments')
    content = models.TextField(blank=False)
    polis_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    approval = models.CharField(
        max_length=32,
        choices=APPROVEMENT_CHOICES,
        default=APPROVEMENT_CHOICES[2][0]
    )

    def __str__(self):
        return self.content

    @property
    def agree_votes(self):
        return self.votes.filter(value=Vote.AGREE).count()

    @property
    def disagree_votes(self):
        return self.votes.filter(value=Vote.DISAGREE).count()

    @property
    def pass_votes(self):
        return self.votes.filter(value=Vote.PASS).count()

    @property
    def total_votes(self):
        return self.votes.count()



class Vote(models.Model):
    AGREE = 1
    PASS = 0
    DISAGREE = -1

    VOTE_CHOICES = (
        (AGREE, _('AGREE')),
        (PASS, _('PASS')),
        (DISAGREE, _('DISAGREE')),
    )

    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='votes')
    comment = models.ForeignKey(Comment, related_name='votes')
    polis_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    value = models.IntegerField(
        blank=False,
        choices=VOTE_CHOICES,
    )

    class Meta:
        unique_together = ("author", "comment")
