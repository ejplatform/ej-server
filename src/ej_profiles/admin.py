from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from . import models


@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    fieldsets = (
        (_('Basic information'), {'fields': [
            'image', 'race', 'gender', 'age', 'occupation',
        ]}),
        (_('Address'), {'fields': [
            'city', 'state', 'country',
        ]}),
        (_('Advanced'), {'fields': [
            'political_activity',
            'biography',
        ]}),
    )
    list_display = ('username', 'name', 'email', 'is_superuser')
    search_fields = ['user__name', 'user__email']
