from django.forms import modelformset_factory, ModelForm, ValidationError
from django.utils.translation import ugettext_lazy as _

from .models import Stereotype, StereotypeVote


class StereotypeForm(ModelForm):
    class Meta:
        model = Stereotype
        fields = ['name', 'description']

    def __init__(self, *args, owner=None, **kwargs):
        super(StereotypeForm, self).__init__(*args, **kwargs)
        self.owner = owner or self.instance.owner

    def clean(self):
        super(StereotypeForm, self).clean()
        name = self.cleaned_data.get('name')
        if self.instance and name == self.instance.name:
            return self.cleaned_data
        elif self._check_stereotype_exists(name):
            msg = _('A stereotype with this name already exists.')
            raise ValidationError(msg)
        return self.cleaned_data

    def save(self, commit=True):
        stereotype = super().save(commit=False)
        stereotype.owner = self.owner
        if commit:
            stereotype.save()
        return stereotype

    def _check_stereotype_exists(self, name):
        return Stereotype.objects.filter(name=name, owner=self.owner).exists()


class StereotypeVoteForm(ModelForm):
    class Meta:
        model = StereotypeVote
        fields = ['comment', 'choice']

    def __init__(self, *args, **kwargs):
        super(StereotypeVoteForm, self).__init__(*args, **kwargs)
        self.fields['comment'].widget.attrs = {'class': 'comment_select'}


StereotypeVoteCreateFormSet = modelformset_factory(
    StereotypeVote,
    form=StereotypeVoteForm,
)

StereotypeVoteEditFormSet = modelformset_factory(
    StereotypeVote,
    form=StereotypeVoteForm,
    extra=0,
)
