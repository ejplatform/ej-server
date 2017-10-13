from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings


class Conversation(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    title = models.CharField(max_length=255, blank=False)
    description = models.TextField(blank=False)
    polis_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    

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
