from django.contrib import admin

from .models import Mission, Comment, Receipt

admin.site.register(Mission)
admin.site.register(Receipt)
admin.site.register(Comment)
