from django.conf import settings

if settings.USE_SQLITE:
    import jsonfield
else:
    import django.contrib.postgres.fields as jsonfield

JSONField = jsonfield.JSONField
