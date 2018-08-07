from django.forms import inlineformset_factory, ModelForm
from .models import Stereotype, StereotypeVote


class StereotypeForm(ModelForm):
    class Meta:
        model = Stereotype
        fields = ['name', 'description']


class StereotypeVoteForm(ModelForm):
    class Meta:
        model = StereotypeVote
        fields = ['comment', 'choice']


StereotypeVoteFormSet = inlineformset_factory(Stereotype, StereotypeVote,
                                              form=StereotypeVoteForm, extra=1)
