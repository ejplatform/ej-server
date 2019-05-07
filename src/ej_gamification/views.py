from django.db.models.functions import Coalesce
from django.contrib.auth import get_user_model
from rest_framework import views, permissions
from django.db.models import Sum
from rest_framework.response import Response
from pinax.points.models import AwardedPointValue


class AwardedPointsView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = self.request.user
        my_points = sum(
            [aw.points for aw in AwardedPointValue.objects.filter(target_user=user)]
        )
        return Response({"status": "success", "points": my_points})


class PointsLeaderBoardView(views.APIView):
    def get(self, request):
        qs = (
            get_user_model()
            .objects.annotate(
                num_points=Coalesce(Sum("awardedpointvalue_targets__points"), 0)
            )
            .order_by("-num_points")[:50]
        )
        response = [
            {
                "name": u.get_full_name() if u.get_full_name() else u.username,
                "points": u.num_points,
            }
            for u in qs
        ]
        return Response({"status": "success", "leaderboard": response})
