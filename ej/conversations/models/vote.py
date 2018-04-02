from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Vote(models.Model):
    """
    A single vote cast for a comment.
    """
    # Be aware this is the opposite of polis. Eg. in polis, agree is -1.
    AGREE = 1
    PASS = 0
    DISAGREE = -1

    VOTE_CHOICES = (
        (AGREE, _('AGREE')),
        (PASS, _('PASS')),
        (DISAGREE, _('DISAGREE')),
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='votes',
        on_delete=models.PROTECT,
    )
    comment = models.ForeignKey(
        'Comment',
        related_name='votes',
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(
        _('Created at'),
        auto_now_add=True,
    )
    value = models.IntegerField(
        _('Value'),
        choices=VOTE_CHOICES,
    )

    class Meta:
        unique_together = ('author', 'comment')

    def save(self, *args, **kwargs):
        super(Vote, self).save(*args, **kwargs)
        self.comment.conversation.update_statistics()
