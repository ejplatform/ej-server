from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings


class Conversation(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    title = models.CharField(max_length=150)
    description = models.TextField(blank=False)
    
class Comment(models.Model):
    conversation = models.ForeignKey(Conversation, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='comments')
    content = models.CharField(max_length=140, blank=False) 

class Vote(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='votes')
    conversation = models.ForeignKey(Conversation, related_name='votes')
    comment = models.ForeignKey(Comment, related_name='votes')
    value = models.IntegerField(
        blank=False,
        validators=[MinValueValidator(-1), MaxValueValidator(1)]
    )

class Participant(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='participations')
    conversation = models.ForeignKey(Conversation, related_name='participants')
