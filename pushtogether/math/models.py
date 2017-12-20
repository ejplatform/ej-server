from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import JSONField, ArrayField

class Job(models.Model):  
    """Class describing a computational job"""

    # currently, available types of job are:
    CLUSTERS = 'CLUSTERS'
    TYPE = (
        (CLUSTERS, _('CLUSTERS')),
    )

    # list of statuses that job can have
    PENDING = 'PENDING'
    STARTED = 'STARTED'
    FINISHED = 'FINISHED'
    FAILED = 'FAILED'
    STATUS = (
        (PENDING, _('PENDING')),
        (STARTED, _('STARTED')),
        (FINISHED, _('FINISHED')),
        (FAILED, _('FAILED')),
    )

    type = models.CharField(choices=TYPE, max_length=20)
    status = models.CharField(choices=STATUS, max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    argument = ArrayField(
        ArrayField(
            models.IntegerField(),
            size=3,
        )
    )
    result = JSONField(null=True)

    def save(self, *args, **kwargs):
        """Save model and if job is in pending state, schedule it"""
        super(Job, self).save(*args, **kwargs)
        if self.status == self.PENDING:
            from .tasks import TASK_MAPPING
            task = TASK_MAPPING[self.type]
            task.delay(job_id=self.id, votes=self.argument)
