from django.forms import modelformset_factory, ModelForm
from .models import Stereotype, StereotypeVote, Cluster, Clusterization
from ej_conversations.models import Conversation


class StereotypeForm(ModelForm):
    class Meta:
        model = Stereotype
        fields = ['name', 'conversation', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['conversation'].queryset = Conversation.objects.none()


class StereotypeVoteForm(ModelForm):
    class Meta:
        model = StereotypeVote
        fields = ['comment', 'choice']


StereotypeVoteFormSet = modelformset_factory(
    StereotypeVote,
    form=StereotypeVoteForm,
)


class ClusterForm(ModelForm):
    class Meta:
        model = Cluster
        fields = ['name', 'stereotypes']


class ClusterizationForm(ModelForm):
    class Meta:
        model = Clusterization
        fields = ['conversation']
