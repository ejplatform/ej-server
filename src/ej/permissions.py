from rest_framework import permissions


class IsAuthor(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True

    def has_object_permission(self, request, view, obj):
        if obj.author == request.user:
            return True

        return False


class IsOwner(permissions.BasePermission):  # For model cluster
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True

    def has_object_permission(self, request, view, obj):
        if obj.owner == request.user:
            return True

        return False


class IsUser(permissions.BasePermission):  # For model profile
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True

    def has_object_permission(self, request, view, obj):
        if obj.user == request.user:
            return True

        return False


class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True

    def has_object_permission(self, request):
        if request.user.is_superuser:
            return True

        return False


class IsAuthenticatedCreationView(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if view.action == "create":
                return True

        return False


class IsAuthenticatedOnlyGetView(permissions.BasePermission):
    def has_permission(self, request, view):
        forbidden_endpoints = ["create", "update", "partial_update", "destroy"]
        if request.user.is_authenticated:
            if view.action in forbidden_endpoints:
                return False

            return True
        return False
