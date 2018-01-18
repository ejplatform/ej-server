from rest_framework import viewsets, views, status, permissions
from django.db.models import Count, Sum
from django.db.models.functions import Coalesce
from django.contrib.auth import get_user_model

from rest_framework.response import Response
from pinax.badges.registry import badges
from pinax.badges.models import BadgeAward
from pinax.points.models import AwardedPointValue


class AwardedPointsView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = self.request.user
        my_points = sum([aw.points for aw in AwardedPointValue.objects.filter(target_user=user)])
        return Response({'status': 'success', 'points': my_points})


class PointsLeaderBoardView(views.APIView):
    def get(self, request):
        qs = get_user_model().objects.annotate(num_points=Coalesce(Sum('awardedpointvalue_targets__points'), 0)).order_by('-num_points')[:50]
        response = [{'name': u.get_full_name() if u.get_full_name() else u.username, 'points': u.num_points} for u in qs]
        return Response({'status': 'success', 'leaderboard': response})

class BadgeViewSet(viewsets.ViewSet):
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request):
        if request.user.is_authenticated():
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

