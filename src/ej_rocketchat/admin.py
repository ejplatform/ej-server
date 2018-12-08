from django.contrib import admin

from . import models

admin.site.register(models.RCConfig)


@admin.register(models.RCAccount)
class RCAccountAdmin(admin.ModelAdmin):
    fields = ['config', 'user', 'username', 'password', 'user_rc_id', 'auth_token', 'is_active']
