import datetime
import logging
import sidekick as sk

timezone = sk.import_later('django.utils.timezone')
models = sk.import_later('.models', package=__package__)
promotions = sk.deferred(lambda: models.CommentPromotion.objects)
powers = sk.deferred(lambda: models.GivenPower.objects)
valid_promotions = sk.deferred(lambda: models.CommentPromotion.timeframed)
DEFAULT_EXPIRATION_TIME_DELTA = datetime.timedelta(hours=24)
log = logging.getLogger('ej')


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
    promotion = promotions.create(comment=comment, promoter=author, end=expires)
    promotion.users.set(users)
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


def give_promotion_power(power_class, user, conversation, users, expires=None):
    """
    description
    Args:
    Returns:
    """
    expires = expires or timezone.now() + DEFAULT_EXPIRATION_TIME_DELTA
    power = power_class(user=user, conversation=conversation, end=expires)

    power.set_affected_users(users)
    power.save()
    return power


def give_minority_power(user, conversation, users, expires=None):
    """
    description
    Args:
    Returns:
    """
    return give_promotion_power(models.GivenMinorityPower, user, conversation, users, expires)


def give_bridge_power(user, conversation, users, expires=None):
    """
    description
    Args:
    Returns:
    """
    return give_promotion_power(models.GivenBridgePower, user, conversation, users, expires)


def clean_expired_promotion_powers():
    expired_qs = powers.filter(end__lte=timezone.now()).get_real_instances()
    size = expired_qs.count()
    if size > 0:
        expired_qs.delete()
        log.info(f'excluded {size} expired promotion powers')
