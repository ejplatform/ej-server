from django import forms
from django.utils.translation import ugettext_lazy as _

from ej.forms import EjForm
from ej_conversations.models import Conversation
from .factories import create_conversations, create_users, random_voters_for_conversation, \
    partition_voters, random_voting_profile, random_votes


class CreateUsersForm(EjForm):
    size = forms.IntegerField(
        label=_('Number of new users'),
        initial=10,
    )
    fill_profile = forms.BooleanField(
        label=_('Fill profile with random data?'),
        required=False,
    )

    def create(self):
        size = self.cleaned_data['size']
        fill_profile = self.cleaned_data['fill_profile']
        create_users(size, fill_profile)


class CreateConversationsForm(EjForm):
    size = forms.IntegerField(
        label=_('Number of new conversations'),
        initial=5,
    )
    comments = forms.IntegerField(
        label=_('Number of comments per conversation'),
        initial=20,
    )

    def create(self):
        data = self.cleaned_data
        create_conversations(data['size'], data['comments'])


class CreateVotesForm(EjForm):
    conversation = forms.ModelChoiceField(
        Conversation.objects.filter(is_hidden=False),
    )
    n_votes = forms.IntegerField(
        label=_('Average number of votes per comment'),
        initial=10,
    )
    n_clusters = forms.IntegerField(
        label=_('Number of clusters/personas'),
        initial=4,
    )

    def create(self):
        data = self.cleaned_data
        conversation = data['conversation']
        comments = conversation.comments.all()
        n_voters = 3 * len(comments)
        voters = random_voters_for_conversation(n_voters, conversation)
        clusters = partition_voters(data['n_clusters'], voters)

        for cluster in clusters:
            persona = random_voting_profile(comments)
            random_votes(n_voters, conversation, cluster, len(cluster), profile=persona)
