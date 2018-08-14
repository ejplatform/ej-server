from django.forms import modelformset_factory, ModelForm
from .models import Stereotype, StereotypeVote, Cluster, Clusterization
from ej_conversations.models import Comment


class StereotypeForm(ModelForm):
    class Meta:
        model = Stereotype
        fields = ['name', 'conversation', 'description']


class StereotypeVoteForm(ModelForm):
    class Meta:
        model = StereotypeVote
        fields = ['comment', 'choice']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['comment'].queryset = Comment.objects.none()


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
