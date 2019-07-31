from collections import defaultdict
from logging import getLogger

from boogie.router import Router
from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _, ugettext as __
from sidekick import import_later

from ej_conversations.models import Conversation
from ej_conversations.routes import conversation_url
from ej_conversations.utils import check_promoted
from ej_profiles.enums import Gender, Race

wordcloud = import_later("wordcloud")
stop_words = import_later("stop_words")
pd = import_later("pandas")
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
    names = getattr(settings, "EJ_PROFILE_FIELD_NAMES", {})
    return {
        "gender_field": names.get("gender", _("Gender")),
        "race_field": names.get("race", _("Race")),
        "conversation": check(conversation, request),
        "pca_link": _("https://en.wikipedia.org/wiki/Principal_component_analysis"),
    }


@urlpatterns.route("scatter/pca.json", template=None)
def scatter_pca_json(request, conversation, slug, check=check_promoted):
    from sklearn.decomposition import PCA
    from sklearn import impute

    check(conversation, request)
    clusterization = getattr(conversation, "clusterization", None)
    if clusterization is not None:
        clusterization.update_clusterization()

    df = conversation.votes.votes_table("mean")
    if df.shape[0] <= 3 or df.shape[1] <= 3:
        return JsonResponse({"error": "InsufficientData", "message": _("Not enough data")})
    pca = PCA(2)
    data = pca.fit_transform(df.values)
    data = pd.DataFrame(data, index=df.index, columns=["x", "y"])
    imputer = impute.SimpleImputer().fit(df.values)

    # Mark self, if found
    if request.user.id in data.index:
        user_coords = data.loc[request.user.id]
    else:
        user_coords = [0, 0]

    # Add extra columns (for now it is hardcoded as name, gender and race)
    # In the future, it might be configurable.
    extra_fields = ["name", "gender", "race"]
    data[extra_fields] = User.objects.filter(id__in=data.index).dataframe(
        *(FIELD_DATA[f]["query"] for f in extra_fields)
    )
    for f in extra_fields:
        data[f] = FIELD_DATA[f].get("transform", lambda x: x)(data[f])

    visual_map = [
        {"dimension": n, **FIELD_DATA[f]["visual_map"]} for n, f in enumerate(extra_fields[1:], 3)
    ]

    # Check clusters
    visual_clusters = {}
    stereotype_coords = []
    visual_map.append(visual_clusters)
    if apps.is_installed("ej_clusters"):
        from ej_clusters.models import Stereotype

        labels = conversation.clusterization.clusters.all().dataframe("name", index="users")
        if labels.shape != (0, 0):
            data["cluster"] = labels
            data["cluster"].fillna(__("*Unknown*"), inplace=True)
            clusters = [*pd.unique(labels.values.flat), _("*Unknown*")]
            visual_clusters.update(
                {
                    **PIECEWISE_OPTIONS,
                    "dimension": len(visual_map) + 2,
                    "categories": clusters,
                    "inRange": {"color": COLORS[: len(clusters)]},
                }
            )

            # Stereotype votes
            stereotypes = conversation.clusters.all().stereotypes()
            names = dict(Stereotype.objects.values_list("id", "name"))
            votes = stereotypes.votes_table()
            missing_cols = set(df.columns) - set(votes.columns)
            for col in missing_cols:
                votes[col] = float("nan")
            votes = votes[list(df.columns)]
            points = pca.transform(imputer.transform(votes))
            stereotype_coords = [
                [x, y, names[pk], None, None, None] for pk, (x, y) in zip(votes.index, points)
            ]

    # Send JSON
    axis_opts = {"axisTick": {"show": False}, "axisLabel": {"show": False}}

    return JsonResponse(
        {
            "option": {
                "legend": {"data": ["all"], "xAxis": "center"},
                "tooltip": {
                    "showDelay": 0,
                    "axisPointer": {
                        "show": True,
                        "type": "cross",
                        "lineStyle": {"type": "dashed", "width": 1},
                    },
                },
                "xAxis": axis_opts,
                "yAxis": axis_opts,
                "series": [
                    {
                        "type": "scatter",
                        "name": _("PCA data"),
                        "symbolSize": 18,
                        "markPoint": {
                            "data": [
                                {
                                    "name": _("You!"),
                                    "coord": [*user_coords, _("You!"), None, None],
                                    "label": {"show": True, "formatter": _("You!")},
                                }
                            ]
                        },
                        "data": data.values.tolist(),
                    },
                    {
                        "type": "effectScatter",
                        "name": _("User and stereotypes"),
                        "color": "#000",
                        "symbolSize": 18,
                        "data": [*stereotype_coords],
                    },
                ],
            },
            "visualMap": visual_map,
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

COLORS = [
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
]
SYMBOLS = ["circle", "rect", "triangle", "diamond", "arrow", "roundRect", "pin"]
FIELD_NAMES = getattr(settings, "EJ_PROFILE_FIELD_NAMES", {})
PIECEWISE_OPTIONS = {
    "piecewise": True,
    "top": "top",
    "orient": "horizontal",
    "padding": [20, 10, 10, 10],
    "outOfRange": {"opacity": 0.25, "colorSaturation": 0.0},
}
FIELD_DATA = {
    "gender": {
        "query": "profile__gender",
        "name": FIELD_NAMES.get("gender", _("Gender")),
        "visual_map": {
            **PIECEWISE_OPTIONS,
            "categories": [x.description for x in Gender if x != 0],
            "inRange": {"color": COLORS[: len(list(Gender))]},
        },
        "transform": lambda col: col.apply(lambda x: (x or None) and Gender(x).description),
    },
    "race": {
        "query": "profile__race",
        "name": FIELD_NAMES.get("race", _("Race")),
        "visual_map": {
            **PIECEWISE_OPTIONS,
            "categories": [x.description for x in Race if x != 0],
            "inRange": {"color": COLORS[: len(list(Race))]},
        },
        "transform": lambda col: col.apply(lambda x: (x or None) and Race(x).description),
    },
    "name": {"query": "name", "name": _("Name")},
}
