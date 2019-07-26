from boogie.router import Router
from django.shortcuts import render

from . import models

app_name = "ej_gamification"
urlpatterns = Router(template="ej_gamification/{name}.jinja2", login=True)
sign = lambda x: 1 if x >= 0 else -1


@urlpatterns.route("achievements/")
def achievements(request):
    user = request.user
    progress = models.get_progress(user, sync=True)

    return {
        "user": user,
        "position_idx": progress.position,
        "n_users": models.UserProgress.objects.count(),
        "n_trophies": progress.n_trophies,
        #
        #  Global achievements
        "progress": progress,
        # "score_level": progress.commenter_level,
        "profile_level": progress.profile_level,
        "commenter_level": progress.commenter_level,
        "host_level": progress.host_level,
        #
        #  Local achievements
        "participation_trophies": user.participation_progresses.all(),
        "conversation_trophies": models.ConversationProgress.objects.filter(conversation__author=user),
    }


@urlpatterns.route("achievements/progress-flag-<int:position>-<int:total>.svg")
def progress_flag(request, position, total):
    alpha = 2
    e = 1e-50
    scale = 137.99982 / 38.45
    start = 0.1
    end = 35.76
    pc = (total - position + e) / (total + e)
    x = 2 * (pc - 0.5)
    pc = 0.5 * sign(x) * x ** alpha + 0.5
    cx = scale * (pc * (end - start) + start)

    return render(
        request, "ej_gamification/progress-flag.jinja2", {"circle_cx": cx}, content_type="image/svg+xml"
    )
