from django.forms import modelformset_factory, ModelForm
from .models import Stereotype, StereotypeVote, Cluster


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
        fields = ['name' ,'stereotypes']