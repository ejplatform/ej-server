import pytest
from ej_gamification import routes


class TestRoutes:
    @pytest.mark.xfail(strict=True, reason="Route not fully implemented")
    def test_badges(self, rf, user):
        request = rf.get("", {})
        request.user = user
        response = routes.badges(request)
        assert response == {"user": user, "badges": user.badges_earned.all()}

    @pytest.mark.xfail(strict=True, reason="Route not fully implemented")
    def test_leaderboard(self, rf, user):
        request = rf.get("", {})
        request.user = user
        response = routes.leaderboard(request)
        assert len(response.items()) > 1

    @pytest.mark.xfail(strict=True, reason="Route not fully implemented")
    def test_powers(self, rf, user):
        request = rf.get("", {})
        request.user = user
        response = routes.powers(request)
        assert len(response.items()) > 1

    @pytest.mark.xfail(strict=True, reason="Route not fully implemented")
    def test_quests(self, rf, user):
        request = rf.get("", {})
        request.user = user
        response = routes.quests(request)
        assert len(response.items()) > 1
