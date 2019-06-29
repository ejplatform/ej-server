from django.apps import apps
from django.utils.translation import ugettext_lazy as _
from sidekick import import_later

from .utils import descr, register_actions

users_recipes = import_later("ej_users.mommy_recipes")

#
# EJ users
#
if apps.is_installed("ej_users"):
    import ej_users.admin

    @register_actions(ej_users.admin.UserAdmin)
    class UserActions:
        @descr(_("dbg: Fill profile randomly"))
        def fill_profiles(self, request, queryset):
            for user in queryset:
                users_recipes.get_random_profile(user).save()
