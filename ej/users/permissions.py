from rest_framework import permissions


class IsCurrentUserOrAdmin(permissions.BasePermission):

    def has_object_permission(self, request, obj):
        if request.user:
            if request.user.is_superuser:
                return True
            else:
                return obj == request.user
        else:
            return False
