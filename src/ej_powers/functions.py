import datetime

import sidekick as sk

timezone = sk.import_later('django.utils.timezone')
models = sk.import_later('.models', package=__package__)
promotions = sk.deferred(lambda: models.CommentPromotion.objects)
valid_promotions = sk.deferred(lambda: models.CommentPromotion.timeframed)
DEFAULT_EXPIRATION_TIME_DELTA = datetime.timedelta(hours=24)


def promote_comment(comment, *, author, users, expires=None):
    """
    Promotes comment for the given users.

    Args:
        comment (Comment):
            Promoted comment.
        author (User):
            Author of the promotion
        users (sequence of users):
            Queryset or sequence of all users that should see the promotion.
        expires (Datetime):
            Optional date in which the promotion expires.

    Returns:
        A CommentPromotion object
    """
    expires = expires or timezone.now() + DEFAULT_EXPIRATION_TIME_DELTA
    promotion = promotions.create(comment=comment, author=author, expires=expires)
    promotion.users.bulk_add(users)
    return promotion


def is_promoted(comment, user):
    """
    Return True if comment is promoted for given user.
    """
    return bool(valid_promotions.filter(comment=comment, users__id=user.id))


def clean_expired_promotions():
    """
    Clean all expired promotions.
    """
    qs = promotions.filter(end__lte=timezone.now())
    size = qs.count()
    if size > 0:
        qs.delete()
        log.info(f'excluded {size} expired promotions')
