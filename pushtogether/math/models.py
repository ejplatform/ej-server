from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import JSONField, ArrayField

from ..conversations.models import Conversation


class Job(models.Model):
    """Class describing a computational job"""

    # currently, available types of job are:
    CLUSTERS = 'CLUSTERS'
    TYPE_CHOICES = (
        (CLUSTERS, _('CLUSTERS')),
    )

    # list of statuses that job can have
    PENDING = 'PENDING'
    STARTED = 'STARTED'
    FINISHED = 'FINISHED'
    FAILED = 'FAILED'
    STATUS_CHOICES = (
        (PENDING, _('PENDING')),
        (STARTED, _('STARTED')),
        (FINISHED, _('FINISHED')),
        (FAILED, _('FAILED')),
    )

    conversation = models.ForeignKey(Conversation, related_name="math_jobs")
    type = models.CharField(_("Type"), choices=TYPE_CHOICES, max_length=20)
    status = models.CharField(
        _("Status"),
        choices=STATUS_CHOICES,
        max_length=20,
        default=STATUS_CHOICES[0][0]
    )
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)
    result = JSONField(null=True)

    def save(self, *args, **kwargs):
        """Save model and if job is in pending state, schedule it"""
        super(Job, self).save(*args, **kwargs)
        if self.status == self.PENDING:
            from .tasks import TASK_MAPPING
            task = TASK_MAPPING[self.type]

            # Avoids the concurrency between celery worker and django core
            # when the core didn't save the Job into the database and the
            # worker tries to access it to change its state.
            transaction.on_commit(
                lambda: task.delay(
                    job_id=self.id,
                    conversation_id=self.conversation.id
                )
            )
