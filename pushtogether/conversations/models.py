import re
from random import randint

from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.db.models import Q

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

    #Conversation's configuration
    comment_nudge = models.IntegerField(null=True, blank=True)
    comment_nudge_interval = models.IntegerField(null=True, blank=True) #seconds
    background_image = models.ImageField(
        upload_to='conversations/images/backgrouds',
        null=True, blank=True)
    background_color = models.CharField(
        max_length=7, validators=[validate_color],
        null=True, blank=True)

    def __str__(self):
        return self.title

    @property
    def total_participants(self):
        return User.objects.filter(votes__comment__conversation_id=self.id).count()

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

        return user_votes/total_approved_comments if total_approved_comments else 0;

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


class Comment(models.Model):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    UNMODERATED = "UNMODERATED"

    APPROVEMENT_CHOICES = (
        (APPROVED, 'approved'),
        (REJECTED, 'rejected'),
        (UNMODERATED, 'unmoderated'),
    )

    conversation = models.ForeignKey(Conversation, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='comments')
    content = models.TextField(blank=False)
    polis_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    approval = models.CharField(
        max_length=32,
        choices=APPROVEMENT_CHOICES,
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
        (AGREE, "AGREE"),
        (PASS, "PASS"),
        (DISAGREE, "DISAGREE"),
    )

    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='votes')
    comment = models.ForeignKey(Comment, related_name='votes')
    polis_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    value = models.IntegerField(
        blank=False,
        choices=VOTE_CHOICES,
    )
