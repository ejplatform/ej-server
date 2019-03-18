from boogie.router import Router

from ej_gamification.models.progress import get_progress

app_name = 'ej_gamification'
urlpatterns = Router(
    template='ej_gamification/{name}.jinja2',
    login=True,
)


@urlpatterns.route('achievements/')
def achievements(request):
    user = request.user
    p = get_progress(user, sync=True)
    return {
        'user': user,
        'achievements': {
            'score': p.score,
            'score_bias': p.score_bias,

            'commenter_level': p.commenter_level,
            'max_commenter_level': p.max_commenter_level,
            'next_commenter_level': p.commenter_level.achieve_next_level_msg(p),

            'host_level': p.host_level,
            'max_host_level': p.max_host_level,
            'next_host_level': p.host_level.achieve_next_level_msg(p),

            'profile_level': p.profile_level,
            'max_profile_level': p.max_profile_level,
            'next_profile_level': p.profile_level.achieve_next_level_msg(p),

            'lvl1_conv': p.n_conversation_lvl_1,
            'lvl2_conv': p.n_conversation_lvl_2,
            'lvl3_conv': p.n_conversation_lvl_3,
            'lvl4_conv': p.n_conversation_lvl_4,

            'n_conversations': p.n_conversations,
            'n_comments': p.n_comments,
            'n_rejected_comments': p.n_rejected_comments,
            'n_votes': p.n_votes,
            'n_endorsements': p.n_endorsements,
            'n_given_opinion_bridge_powers': p.n_given_opinion_bridge_powers,
            'n_given_minority_activist_powers': p.n_given_minority_activist_powers,
            'total_conversation_score': p.total_conversation_score,
            'total_participation_score': p.total_participation_score,
        }
    }


@urlpatterns.route('powers/')
def powers(request):
    user = request.user
    return {
        'user': user,
    }


@urlpatterns.route('quests/')
def quests(request):
    user = request.user
    return {
        'user': user,
    }
