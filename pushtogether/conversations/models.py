import re

from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings

from .validators import validate_color
    

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

    def get_user_participation_ratio(self, user):
        total_votes = Vote.objects.filter(
            comment__conversation_id=self.id).count()
        user_votes = Vote.objects.filter(
            comment__conversation_id=self.id,
            author=user).count()

        return user_votes/total_votes if total_votes else 0;
    

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
