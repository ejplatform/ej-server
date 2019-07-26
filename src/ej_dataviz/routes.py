from collections import defaultdict
from logging import getLogger

from boogie.router import Router
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _
from sidekick import import_later

from ej_conversations.models import Conversation
from ej_conversations.routes import conversation_url
from ej_conversations.utils import check_promoted
from ej_profiles.enums import Gender, Race

wordcloud = import_later("wordcloud")
stop_words = import_later("stop_words")
log = getLogger("ej")

urlpatterns = Router(
    base_path=conversation_url,
    template="ej_dataviz/{name}.jinja2",
    models={"conversation": Conversation},
    login=True,
)
app_name = "ej_dataviz"
User = get_user_model()


#
# Scatter plot
#
@urlpatterns.route("scatter/")
def scatter(request, conversation, slug, check=check_promoted):
    return {
        "conversation": check(conversation, request),
        "pca_link": _("https://en.wikipedia.org/wiki/Principal_component_analysis"),
    }


@urlpatterns.route("scatter/pca.json", template=None)
def scatter_pca_json(request, conversation, slug, check=check_promoted):
    from sklearn.decomposition import PCA

    check(conversation, request)
    df = conversation.votes.votes_table("mean")
    if df.shape[0] <= 3 or df.shape[1] <= 3:
        return JsonResponse({"error": "InsufficientData", "message": _("Not enough data")})

    data = PCA(2).fit_transform(df.values)
    axis_opts = {"axisTick": {"show": False}, "axisLabel": {"show": False}}
    return JsonResponse(
        {
            "option": {
                "xAxis": axis_opts,
                "yAxis": axis_opts,
                "color": [
                    "#042A46",
                    "#FF3E72",
                    "#30BFD3",
                    "#36C273",
                    "#7758B3",
                    "#797979",
                    "#F68128",
                    "#C4F2F4",
                    "#B4FDD4",
                    "#FFE1CA",
                    "#E7DBFF",
                    "#FFE3EA",
                    "#EEEEEE",
                ],
                "series": [{"symbolSize": 16, "data": data.tolist(), "type": "scatter"}],
            },
            "userIds": df.index.tolist(),
        }
    )


@urlpatterns.route("scatter/group-<groupby>.json")
def scatter_group(request, conversation, slug, groupby, check=check_promoted):
    check(conversation, request)
    if groupby not in VALID_GROUP_BY:
        return JsonResponse({"error": "AttributeError", "message": "invalid groupby parameter"})
    param = VALID_GROUP_BY[groupby]

    # Process raw data to form clusters
    data_pairs = User.objects.filter(votes__comment__conversation=conversation).values_list("id", param)

    data = defaultdict(list)
    for user, value in data_pairs:
        data[value].append(user)

    name_transform = GROUP_NAMES[groupby]
    description_transform = GROUP_DESCRIPTIONS[groupby]
    return JsonResponse(
        {
            "groups": {name_transform(k): v for k, v in data.items()},
            "descriptions": {name_transform(k): description_transform(k) for k in data},
            "groupby": groupby,
        }
    )


#
# Word cloud
#
@urlpatterns.route("word-cloud/")
def word_cloud(request, conversation, slug, check=check_promoted):
    check(conversation, request)
    return {"conversation": conversation}


@urlpatterns.route("word-cloud/words.json")
def words(request, conversation, slug, check=check_promoted):
    check(conversation, request)

    data = "\n".join(conversation.approved_comments.values_list("content", flat=True))
    regexp = r"\w[\w'\u0327]+"
    wc = wordcloud.WordCloud(stopwords=get_stop_words(), regexp=regexp)
    cloud = sorted(wc.process_text(data).items(), key=lambda x: -x[1])[:50]
    return JsonResponse({"cloud": cloud})


#
# Utilities
#
def get_stop_words():
    lang = getattr(settings, "LANGUAGE_CODE", "en")
    lang = NORMALIZE_LANGUAGES.get(lang, lang)
    if lang in stop_words.AVAILABLE_LANGUAGES:
        return stop_words.get_stop_words(lang)

    pre_lang = lang.split("-")[0]
    pre_lang = NORMALIZE_LANGUAGES.get(pre_lang, pre_lang)
    if pre_lang in stop_words.AVAILABLE_LANGUAGES:
        return stop_words.get_stop_words(lang.split("-")[0])

    log.error("Could not find stop words for language {lang!r}. Using English.")
    return stop_words.get_stop_words("en")


#
# Grouping constants
#
VALID_GROUP_BY = {"gender": "profile__gender", "race": "profile__race"}

GROUP_NAMES = {
    "gender": lambda x: None if x is None else Gender(x).name.lower(),
    "race": lambda x: None if x is None else Race(x).name.lower(),
}

GROUP_DESCRIPTIONS = {
    "gender": lambda x: None if x is None else Gender(x).description,
    "race": lambda x: None if x is None else Race(x).description,
}

EXPOSED_PROFILE_FIELDS = ("race", "gender", "age", "occupation", "education", "country", "state")

NORMALIZE_LANGUAGES = {
    "de": "german",
    "fr": "french",
    "en": "english",
    "es": "spanish",
    "it": "italian",
    "pt": "portuguese",
    # TODO: discover correct language codes
    # 'ar': 'arabic',
    # 'bu': 'bulgarian',
    # 'ca': 'catalan',
    # 'cz': 'czech',
    # 'da': 'danish',
    # 'du': 'dutch',
    # 'fi': 'finnish',
    # 'hi': 'hindi',
    # 'hu': 'hungarian',
    # 'in': 'indonesian',
    # 'no': 'norwegian',
    # 'po': 'polish',
    # 'ro': 'romanian',
    # 'ru': 'russian',
    # 'sl': 'slovak',
    # 'sw': 'swedish',
    # 'tu': 'turkish',
    # 'uk': 'ukrainian',
    # 'vi': 'vietnamese',
}
