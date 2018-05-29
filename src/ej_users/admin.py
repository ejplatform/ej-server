from copy import deepcopy

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(AuthUserAdmin):
    list_display = ('username', 'name', 'email', 'is_superuser')
    search_fields = ['name', 'email', 'username']

    # Very ugly code to remove first_name and last_name and replace them by name
    fieldsets = deepcopy(AuthUserAdmin.fieldsets)
    fieldsets[1][1]['fields'] = ['name', *fieldsets[1][1]['fields'][2:]]
