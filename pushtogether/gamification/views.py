from rest_framework import viewsets, views, status, permissions
from pinax.badges.models import BadgeAward
from django.db.models import Count, Sum
from django.db.models.functions import Coalesce
from collections import defaultdict
from rest_framework.response import Response
from pinax.badges.registry import badges
from pinax.points.models import AwardedPointValue
from django.contrib.auth import get_user_model


class AwardedPointsView(views.APIView):
    def get(self, request):
        user = self.request.user
        if user.is_authenticated():
            my_points = sum([aw.points for aw in AwardedPointValue.objects.filter(target_user=user)])
            return Response({'status': 'success', 'points': my_points})
        else:
            return Response({'status': 'error', 'message': _('You are not logged in')},
                            status=status.HTTP_401_UNAUTHORIZED)


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

        badges_awarded = BadgeAward.objects.values("slug", "level").annotate(num=Count("pk"))
        badges_dict = defaultdict(list)
        for badge in badges_awarded:
            if (badge["slug"], badge["level"]) in user_badges:
                badges_dict[badge["slug"]].append({
                    "level": badge["level"],
                    "name": badges._registry[badge["slug"]].levels[badge["level"]].name,
                    "description": badges._registry[badge["slug"]].levels[badge["level"]].description,
                    # "count": badge["num"],
                    "user_has": (badge["slug"], badge["level"]) in user_badges
                })

        for badge_group in badges_dict.values():
            badge_group.sort(key=lambda o: o["level"])

        return Response({"badges": sorted(badges_dict.items())})

