from django.forms import modelformset_factory, ModelForm
from .models import Stereotype, StereotypeVote, Cluster, Clusterization


class StereotypeForm(ModelForm):
    class Meta:
        model = Stereotype
        fields = ['name', 'description']


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
