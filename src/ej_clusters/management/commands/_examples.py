"""
A few functions for creating plausible synthetic data.
"""

from django.contrib.auth import get_user_model

from ej_clusters.factories import set_clusters_from_comments
from ej_conversations import create_conversation


User = get_user_model()


def make_clusters(verbose=True):
    conversation = create_conversation(
        'How should our society organize the production of goods and services?',
        'Economy',
        is_promoted=True,
        author=User.objects.filter(is_staff=True).first(),
    )
    set_clusters_from_comments(conversation, {
        'Liberal': [
            'Free market should regulate how enterprises invest money and hire '
            'employees.',
            'State should provide a stable judicial system and refrain from '
            'regulating the economy.',
        ],
        'Socialist': [
            'Government and the society as a whole must regulate business '
            'decisions to favor the common good rather than private interests.',
            'State leadership is necessary to drive a strong economy.',
        ],
        'Facist': [
            'Government should elliminate opposition in order to ensure '
            'governability.',
            'Military should occupy high ranks in government.',
        ]
    })
