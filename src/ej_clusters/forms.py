from django.forms import (
    modelformset_factory,
    ModelForm,
    CharField,
    TextInput,
    MultipleChoiceField,
    CheckboxSelectMultiple
)
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
    def __init__(self, *args, **kwargs):
        super(ClusterForm, self).__init__(*args, **kwargs)
        self.fields['stereotypes'].choices = self.get_choices()

    def get_choices(self):
        return Stereotype.objects.all().values_list('id', 'name')

    name = CharField(label='name', widget=TextInput(attrs={'placeholder': 'Cluster Name'}))
    stereotypes = MultipleChoiceField(
        widget=CheckboxSelectMultiple,
        choices=[]
    )

    class Meta:
        model = Cluster
        fields = ['name', 'stereotypes']


class ClusterizationForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ClusterizationForm, self).__init__(*args, **kwargs)
        self.fields['conversation'].empty_label = 'Conversation Cluster'
        print(self.fields['conversation'])

    class Meta:
        model = Clusterization
        fields = ['conversation']
