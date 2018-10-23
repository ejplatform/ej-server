import numpy as np
import pandas as pd
import json

from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _, ugettext as __

from boogie.router import Router
from hyperpython.components import html_table
from ej_clusters.math import get_votes
from ej_conversations.models import Conversation
from ej_dataviz import render_dataframe
from ej_math import VoteStats
from ej_profiles.choices import Gender

from sklearn.decomposition import PCA


urlpatterns = Router(
    template='ej_dataviz/{name}.jinja2',
    object='conversation',
    models={
        'conversation': Conversation,
    },
    lookup_field='slug',
    lookup_type='slug',
    login=True,
)
User = get_user_model()
GENDER_CHOICES = list(Gender)


def generate_scatter(request, conversation):
    users_by_gender = list(User.objects.values_list('raw_profile__gender'))

    votes = get_votes(conversation)
    votes = votes.where((pd.notnull(votes)), 0.0)

    pca = PCA(n_components=2)
    pca.fit(votes)
    votes_data = pca.transform(votes)

    votes_data = votes_data.tolist()
    real_data = {}

    for person in range(len(users_by_gender)):
        new_gender_value = 19
        if users_by_gender[person][0] is not None:
            new_gender_value = users_by_gender[person][0]
        if Gender(new_gender_value) not in real_data.keys():
            real_data[Gender(new_gender_value)] = []
        votes_data[person].append(Gender(new_gender_value))
        real_data[Gender(new_gender_value)].append(votes_data[person])

    data = []
    for item in real_data:
        data.append(real_data[item])
        # data[item].append(real_data[item])
    js_data = json.dumps(real_data)
    print(js_data)

    gender_list = []
    for item in GENDER_CHOICES:
        gender_list.append(item)
    print(gender_list)

    js_gender = json.dumps(gender_list)


    response = {'plot_data': js_data, 'js_gender': js_gender}
    return response


#
# Auxiliary functions and data
#
COLUMN_NAMES = {
    'author': _('Author'),
    'text': _('Text'),
    'votes': _('Votes'),
    'missing': _('Missing'),
    'skipped': _('Skipped'),
    'agree': _('Agree'),
    'disagree': _('Disagree'),
    'average': _('Average'),
    'divergence': _('Divergence'),
    'entropy': _('Entropy'),
    'comment': _('Comment'),
    'user': _('User'),
    'participation': _('Participation ratio'),
    'name': _('Name'),
}
PC_COLUMNS = [
    'missing', 'skipped', 'agree', 'disagree', 'average',
    'divergence', 'entropy', 'participation',
]


def map_to_table(data):
    return np.array(list(data.items())).T


def map_to_html_table(cols):
    array = map_to_table(cols)
    cols, body = array
    cols = [__(col) for col in cols]
    return html_table([body], columns=cols, class_='ReportTable table')


def df_to_table(df, pc=True):
    if pc:
        for col in PC_COLUMNS:
            if col in df:
                df[col] = to_pc(df[col])
    return render_dataframe(df, col_display=COLUMN_NAMES, class_='table long')


def to_pc(data):
    """
    Map floats to percentages.
    """

    def transform(x):
        if isinstance(x, int):
            return str(x)
        elif np.isnan(x):
            return '-'
        else:
            return '%d%%' % x

    return list(map(transform, data))


def cluster_comments_table(cluster):
    usernames = list(cluster.users.all().values_list('email', flat=True))

    # Filter votes by users present in cluster
    df = cluster.all_votes
    votes = df[df['user'].isin(usernames)]

    data = comments_table(cluster.conversation, votes)
    data = data.sort_values('agree', ascending=False)
    return df_to_table(data)


def comments_table(conversation, votes):
    """
    Data frame with information about each comment in conversation.
    """

    stats = VoteStats(votes)
    df = stats.comments(pc=True)
    comments = conversation.comments.approved().display_dataframe()
    comments = comments[['author', 'text']]
    for col in ['agree', 'disagree', 'skipped', 'divergence']:
        comments[col] = df[col]
    comments['participation'] = 100 - df['missing']
    comments.dropna(inplace=True)
    return comments


def participants_table(conversation, votes):
    """
    Data frame with information about each participant in conversation.
    """

    stats = VoteStats(votes)
    df = stats.users(pc=True)

    data = list(User.objects.values_list('id', 'email', 'name'))
    moredata = list(User.objects.values_list('id', 'raw_profile__gender'))
    print(moredata)
    participants = pd.DataFrame(list(data), columns=['id', 'email', 'name'])
    participants.index = participants.pop('email')

    for col in ['agree', 'disagree', 'skipped', 'divergence']:
        participants[col] = df[col]

    return participants
