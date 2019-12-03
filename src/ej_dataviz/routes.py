from collections import defaultdict
from logging import getLogger
from typing import Callable, Sequence

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
from ej_profiles.enums import Gender, Race, STATE_CHOICES

np = import_later("numpy")

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

def update_cluster(check, conversation):
    clusterization = getattr(conversation, "clusterization", None)
    if clusterization is not None:
        clusterization.update_clusterization()

def error_response(conversation):
    df = conversation.votes.votes_table("mean")
    if df.shape[0] <= 3 or df.shape[1] <= 3:
        return JsonResponse({"error": "InsufficientData", "message": _("Not enough data")})

@urlpatterns.route("scatter/pca.json", template=None)
def scatter_pca_json(request, conversation, slug, check=check_promoted):
    from sklearn.decomposition import PCA
    from sklearn import impute

    kwargs = {}
    check(conversation, request)

    update_cluster(check, conversation)
    
    error_response(conversation)
    
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
    extra_fields = ["name", "gender", "race", "state"]
    kwargs["extra_fields"] = extra_fields
    data[extra_fields] = User.objects.filter(id__in=data.index).dataframe(
        *(FIELD_DATA[f]["query"] for f in extra_fields)
    )
    for f in extra_fields:
        data[f] = FIELD_DATA[f].get("transform", lambda x: x)(data[f])

    # Check clusters
    stereotype_coords = list(
        create_stereotype_coords(
            conversation,
            data,
            list(df.columns),
            transformer=lambda x: pca.transform(imputer.transform(x)),
            kwargs=kwargs,
        )
    )
    return format_echarts_option(data, user_coords, stereotype_coords, **kwargs)


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
# Auxiliary functions
#
def create_stereotype_coords(conversation, table, comments: list, transformer: Callable, kwargs: dict):
    if apps.is_installed("ej_clusters") and getattr(conversation, "clusterization", None):
        from ej_clusters.models import Stereotype

        labels = conversation.clusterization.clusters.all().dataframe("name", index="users")
        if labels.shape != (0, 0):
            table["cluster"] = labels
            table["cluster"].fillna(__("*Unknown*"), inplace=True)
            kwargs["labels"] = labels

            # Stereotype votes
            stereotypes = conversation.clusters.all().stereotypes()
            names = dict(Stereotype.objects.values_list("id", "name"))
            votes_ = stereotypes.votes_table()
            missing_cols = set(comments) - set(votes_.columns)
            for col in missing_cols:
                votes_[col] = float("nan")
            votes_ = votes_[comments]
            points = transformer(votes_)

            for pk, (x, y) in zip(votes_.index, points):
                yield {
                    "name": names[pk],
                    "symbol": "circle",
                    "coord": [x, y, names[pk], None, None],
                    "label": {"show": True, "formatter": names[pk], "color": "black"},
                    "itemStyle": {"opacity": 0.75, "color": "rgba(180, 180, 180, 0.33)"},
                    "tooltip": {"formatter": _("{} persona").format(names[pk])},
                }


def format_echarts_option(data, user_coords, stereotype_coords, extra_fields: list, labels=None):
    """
    Format option JSON for echarts.
    """
    visual_map = [
        {"dimension": n, **FIELD_DATA[f]["visual_map"]} for n, f in enumerate(extra_fields[1:], 3)
    ]
    if labels is not None:
        clusters = [*pd.unique(labels.values.flat), _("*Unknown*")]
        visual_map.append(
            {
                **PIECEWISE_OPTIONS,
                "dimension": len(visual_map) + 3,
                "categories": clusters,
                "inRange": {"color": COLORS[: len(clusters)]},
            }
        )

    axis_opts = {"axisTick": {"show": False}, "axisLabel": {"show": False}}
    return JsonResponse(
        {
            "option": {
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
                                    "itemStyle": {"color": "black"},
                                    "tooltip": {"formatter": _("You!")},
                                },
                                *stereotype_coords,
                            ]
                        },
                        "data": data.values.tolist(),
                    }
                ],
            },
            "visualMap": visual_map,
        }
    )


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
def field_descriptor(enum):
    def formatter(x):
        if isinstance(x, str):
            return x
        elif x is None or x == 0 or np.isnan(x):
            return None
        else:
            return enum(x).description

    return formatter


def get_state_colors(states: Sequence):
    keys = set(states)
    keys.discard("")

    # We try to infer better colors for special configurations
    # For now, only Brazil is supported. It colors according to geographic region.
    if is_brazil(keys):
        cmap = state_colors_brazil(*COLORS[:5])
        return [cmap[st] for st in states]

    # Generic procedure: 1 color per state
    colors = COLORS[:]
    while len(colors) < len(states):
        colors.extend(COLORS)
    return colors[: len(states)]


def is_brazil(states: set):
    return states == {
        "AC",
        "AL",
        "AP",
        "AM",
        "BA",
        "CE",
        "DF",
        "ES",
        "GO",
        "MA",
        "MT",
        "MS",
        "MG",
        "PA",
        "PB",
        "PR",
        "PE",
        "PI",
        "RJ",
        "RN",
        "RS",
        "RO",
        "RR",
        "SC",
        "SP",
        "SE",
        "TO",
    }


def state_colors_brazil(N, NE, CW, SE, S):
    return {
        "AC": N,
        "AL": NE,
        "AP": N,
        "AM": N,
        "BA": NE,
        "CE": NE,
        "DF": CW,
        "ES": SE,
        "GO": CW,
        "MA": NE,
        "MT": CW,
        "MS": CW,
        "MG": SE,
        "PA": N,
        "PB": NE,
        "PR": S,
        "PE": NE,
        "PI": NE,
        "RJ": SE,
        "RN": NE,
        "RS": S,
        "RO": N,
        "RR": N,
        "SC": S,
        "SP": SE,
        "SE": NE,
        "TO": CW,
    }


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

# Reference: https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
NORMALIZE_LANGUAGES = {
    "ar": "arabic",
    "bg": "bulgarian",
    "ca": "catalan",
    "cs": "czech",
    "da": "danish",
    "de": "german",
    "en": "english",
    "es": "spanish",
    "fi": "finnish",
    "fr": "french",
    "hi": "hindi",
    "hu": "hungarian",
    "id": "indonesian",
    "it": "italian",
    "nl": "dutch",
    "no": "norwegian",
    "pl": "polish",
    "pt": "portuguese",
    "ro": "romanian",
    "ru": "russian",
    "sk": "slovak",
    "sv": "swedish",
    "tr": "turkish",
    "uk": "ukrainian",
    "vi": "vietnamese",
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
VALID_STATE_CHOICES = sorted((st for st, _ in STATE_CHOICES if st))
FIELD_DATA = {
    "gender": {
        "query": "profile__gender",
        "name": FIELD_NAMES.get("gender", _("Gender")),
        "visual_map": {
            **PIECEWISE_OPTIONS,
            "categories": [x.description for x in Gender if x != 0],
            "inRange": {"color": COLORS[: len(list(Gender))]},
        },
        "transform": lambda col: col.apply(field_descriptor(Gender)),
    },
    "race": {
        "query": "profile__race",
        "name": FIELD_NAMES.get("race", _("Race")),
        "visual_map": {
            **PIECEWISE_OPTIONS,
            "categories": [x.description for x in Race if x != 0],
            "inRange": {"color": COLORS[: len(list(Race))]},
        },
        "transform": lambda col: col.apply(field_descriptor(Race)),
    },
    "state": {
        "query": "profile__state",
        "name": FIELD_NAMES.get("state", _("State")),
        "visual_map": {
            "piecewise": True,
            "padding": [20, 5, 5, 10],
            "top": "center",
            "outOfRange": PIECEWISE_OPTIONS["outOfRange"],
            "categories": VALID_STATE_CHOICES,
            "inRange": {"color": get_state_colors(VALID_STATE_CHOICES)},
            "itemGap": 2,
            "textStyle": {"fontSize": 8},
            "legend": {"type": "scroll"},
        },
        "transform": lambda x: x,
    },
    "name": {"query": "name", "name": _("Name")},
}
