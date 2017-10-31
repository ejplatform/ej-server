import re
import datetime

from django.utils.timezone import make_aware, get_current_timezone

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

COLOR_RE = re.compile(r'^\#[0-9A-Fa-f]{6}$')

def validate_color(color):
    if not COLOR_RE.match(color):
        raise ValidationError(_("{color} is a bad color", color=color))

def validate_comment_nudge(comment):
    '''
    User cannot write too many comments.
    The limit is set by the conversation's comment_nudge and
    comment_nudge_interval
    '''
    nudge_interval = comment.conversation.comment_nudge_interval
    timedelta = datetime.timedelta(seconds=nudge_interval)
    time_limit = datetime.datetime.now() - timedelta
    aware_time_limit = make_aware(time_limit, get_current_timezone())
    nudge_interval_comments_counter = comment.author.comments.filter(
        created_at__gt = aware_time_limit).count()

    if(nudge_interval_comments_counter >= comment.conversation.comment_nudge):
        raise ValidationError(_("You can't write too many comments"))
