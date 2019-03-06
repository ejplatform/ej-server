from django.forms import modelformset_factory, ModelForm

from ej.forms import EjModelForm
from .models import Stereotype, StereotypeVote


class StereotypeForm(EjModelForm):
    """
    Create and edit new stereotypes
    """

    class Meta:
        # We have to add the owner attribute to enable the unique owner + name
        # validation constraint. This is not ideal since we have to fake the
        # existence of this field using default values
        model = Stereotype
        fields = ['name', 'description', 'owner']

    def __init__(self, *args, owner=None, instance=None, **kwargs):
        self.owner_instance = owner = owner or instance.owner
        kwargs['instance'] = instance
        kwargs['initial'] = {'owner': owner, **kwargs.get('initial', {})}
        super(StereotypeForm, self).__init__(*args, **kwargs)

    def full_clean(self):
        self.data = self.data.copy()
        self.data['owner'] = str(self.owner_instance.id)
        return super().full_clean()


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
