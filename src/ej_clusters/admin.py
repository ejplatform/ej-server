from django.contrib import admin

from . import models

admin.site.register(models.Cluster)
admin.site.register(models.Stereotype)
admin.site.register(models.StereotypeVote)
