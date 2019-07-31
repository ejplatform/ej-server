from operator import attrgetter as attr

from boogie.models import F
from boogie.router import Router
from django.shortcuts import render
from django.utils.translation import ugettext as _
from sidekick import import_later

from ej_dataviz.roles import render_dataframe
from . import models

app_name = "ej_gamification"
urlpatterns = Router(template="ej_gamification/{name}.jinja2", login=True)
sign = lambda x: 1 if x >= 0 else -1
pd = import_later("pandas")


@urlpatterns.route("achievements/")
def achievements(request):
    user = request.user
    progress = models.get_progress(user, sync=True)

    # Leaderboard
    users_before = list(
        reversed(
            models.UserProgress.objects.filter(score__gt=progress.score)
            .order_by("score")
            .values_list("user__name", "score")[:4]
        )
    )

    users_after = list(
        models.UserProgress.objects.filter(score__lte=progress.score)
        .exclude(user_id=user.id)
        .order_by("-score")
        .values_list("user__name", "score")[: 9 - len(users_before)]
    )

    # Trophies
    conversation_trophies = list(
        models.ConversationProgress.objects.filter(conversation__author=user).order_by(
            "-conversation_level"
        )
    )
    participation_trophies = list(
        user.participation_progresses.exclude(conversation__author=F.user).order_by("-voter_level")
    )

    return {
        "user": user,
        "position_idx": progress.position,
        "n_users": models.UserProgress.objects.count(),
        "n_trophies": progress.n_trophies,
        # Leaderboard
        "users_before": users_before,
        "users_after": users_after,
        #  Global achievements
        "progress": progress,
        "score_level": progress.score_level,
        "profile_level": progress.profile_level,
        "commenter_level": progress.commenter_level,
        "host_level": progress.host_level,
        #  Local achievements
        "participation_trophies": participation_trophies,
        "conversation_trophies": conversation_trophies,
    }


@urlpatterns.route("achievements/progress-flag-<int:position>-<int:total>.svg")
def progress_flag(request, position, total):
    total -= 1
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


@urlpatterns.route("leaderboard/", staff=True)
def leaderboard(request):
    scores = models.UserProgress.objects.filter(score__gt=0).order_by("-score")
    fns = {
        _("Name"): attr("user.name"),
        _("Score"): attr("score"),
        _("Votes"): attr("n_final_votes"),
        _("Comments"): attr("n_approved_comments"),
        _("Rejected"): attr("n_rejected_comments"),
        _("pts"): lambda x: x.pts_approved_comments - x.pts_rejected_comments,
        _("Conversation"): attr("total_conversation_score"),
    }
    return {
        "leaderboard": render_dataframe(
            pd.DataFrame([[f(p) for f in fns.values()] for p in scores], columns=fns.keys()), class_="table"
        )
    }


@urlpatterns.route("leaderboard/conversations/", staff=True, template="ej_gamification/leaderboard.jinja2")
def leaderboard_conversations(request):
    scores = models.ConversationProgress.objects.filter(score__gt=0).order_by("-score")
    fns = {
        _("Name"): attr("conversation.title"),
        _("Author"): attr("conversation.author.name"),
        _("Score"): attr("score"),
        _("Votes"): attr("n_final_votes"),
        _("Comments"): attr("n_approved_comments"),
        _("Rejected"): attr("n_rejected_comments"),
        _("pts"): lambda x: x.pts_approved_comments - x.pts_rejected_comments,
    }
    return {
        "leaderboard": render_dataframe(
            pd.DataFrame([[f(p) for f in fns.values()] for p in scores], columns=fns.keys()), class_="table"
        )
    }
