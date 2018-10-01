from django.forms import modelformset_factory, ModelForm, ValidationError
from django.utils.translation import ugettext_lazy as _
from .models import Stereotype, StereotypeVote


class StereotypeForm(ModelForm):
    class Meta:
        model = Stereotype
        fields = ['name', 'description']

    def __init__(self, *args, **kwargs):
        self.conversation = kwargs.pop("conversation")
        super(StereotypeForm, self).__init__(*args, **kwargs)

    def clean(self):
        super(StereotypeForm, self).clean()
        name = self.cleaned_data.get('name')
        stereotype_exists = Stereotype.objects.filter(name=name, conversation=self.conversation).exists()
        if self.instance and name == self.instance.name:
            return self.cleaned_data
        elif stereotype_exists:
            msg = _('Stereotype for this conversation with this name already exists.')
            raise ValidationError(msg)
        return self.cleaned_data


class StereotypeVoteForm(ModelForm):
    class Meta:
        model = StereotypeVote
        fields = ['comment', 'choice']

    def __init__(self, *args, **kwargs):
        super(StereotypeVoteForm, self).__init__(*args, **kwargs)
        self.fields['comment'].widget.attrs = {'class': 'comment_select'}


StereotypeVoteFormSet = modelformset_factory(
    StereotypeVote,
    form=StereotypeVoteForm,
)
