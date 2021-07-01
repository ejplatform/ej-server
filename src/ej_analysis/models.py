from django.db import models


class OpinionComponent(models.Model):
    conversation = models.ForeignKey(
        "ej_conversations.Conversation", on_delete=models.CASCADE, related_name="conversation"
    )
    analytics_property_id = models.CharField(max_length=100, blank=True, null=True)
