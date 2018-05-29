from django.utils import timezone
from django.db.models.signals import class_prepared
from django.dispatch import receiver


def fix():
    """
    Support to timezones in Pinax points
    """

    @receiver(class_prepared, sender='points.AwardedPointValue')
    def fix_model(sender, **kwargs):
        field = sender._meta.get_field('timestamp')
        field.default = timezone.now
