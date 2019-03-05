from boogie.rest import rest_api
from . import models


@rest_api.property(models.SocialMediaIcon)
def fa_class(obj):
    return obj.fa_class
