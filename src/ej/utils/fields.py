from django.conf import settings

if settings.USING_SQLITE:
    import jsonfield
else:
    import django.contrib.postgres.fields as jsonfield

JSONField = jsonfield.JSONField
