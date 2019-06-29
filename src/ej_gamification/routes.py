from boogie.router import Router
from django.shortcuts import render

from ej_gamification.models.progress import (
    get_progress,
    UserProgress,
    ConversationProgress,
)
from .roles import (
    profile_trophy,
    participation_trophy,
    host_trophy,
    participate_conversation_trophy,
    host_conversation_trophy,
)

app_name = "ej_gamification"
urlpatterns = Router(template="ej_gamification/{name}.jinja2", login=True)
sign = lambda x: 1 if x >= 0 else -1


@urlpatterns.route("achievements/")
def achievements(request):
    user = request.user
    progress = get_progress(user, sync=True)
    participation = map(
        participate_conversation_trophy, user.participation_progresses.all()
    )
    conversation_trophies = map(
        host_conversation_trophy,
        ConversationProgress.objects.filter(conversation__author=user),
    )

    return {
        "user": user,
        "progress": progress,
        "position_idx": progress.position,
        "n_users": UserProgress.objects.count(),
        "n_trophies": progress.n_trophies,
        "participation_trophies": participation,
        "conversation_trophies": conversation_trophies,
        "profile_trophy": profile_trophy(progress),
        "participation_trophy": participation_trophy(progress),
        "host_trophy": host_trophy(progress),
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
        request,
        "ej_gamification/progress-flag.jinja2",
        {"circle_cx": cx},
        content_type="image/svg+xml",
    )


@urlpatterns.route("powers/")
def powers(request):
    user = request.user
    return {"user": user}


@urlpatterns.route("quests/")
def quests(request):
    user = request.user
    return {"user": user}
