from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.utils.translation import ugettext_lazy as _
from sidekick import import_later

from .models import User

descr = lambda msg: lambda f: setattr(f, "short_description", msg) or f
recipes = import_later(".mommy_recipes", package=__package__)


@admin.register(User)
class UserAdmin(AuthUserAdmin):
    list_display = ("name", "email", "is_superuser")
    fieldsets = (
        (None, {"fields": ("email", "name", "display_name", "password")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "name", "password1", "password2"),
            },
        ),
    )
    search_fields = ["name", "email"]
    ordering = ["email"]
    actions = ["fill_profiles"]

    #
    # Debug actions
    #
    @descr(_("dbg: Fill profile randomly"))
    def fill_profiles(self, request, queryset):
        for user in queryset:
            recipes.get_random_profile(user).save()
