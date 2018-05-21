from pinax.badges.models import BadgeAward
from pinax.badges.registry import badges
from rest_framework import viewsets, permissions
from rest_framework.response import Response


class BadgeViewSet(viewsets.ViewSet):
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request):
        if request.user.is_authenticated:
            user_badges = set(
                (slug, level) for slug, level in
                BadgeAward.objects.filter(user=request.user).values_list("slug", "level")
            )
        else:
            user_badges = []

        all_badges = badges._registry
        badges_dict = []
        for key, badge in all_badges.items():
            badges_dict.append({
                "slug": badge.slug,
                "levels": [{
                    "level": i,
                    "name": level.name,
                    "description": level.description,
                    "user_has": (badge.slug, i) in user_badges
                } for i, level in enumerate(badge.levels)]
            })
        return Response(badges_dict)
