from django.conf import settings

if settings.USE_SQLITE:
    from jsonfield import JSONField
else:
    from django.contrib.postgres.fields import JSONField
