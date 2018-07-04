from django.forms import ModelForm

from . import models


class TrophyForm(ModelForm):
    """
    Trophy form
    """

    class Meta:
        model = models.Trophy
        fields = [
            'key', 'name', 'short_description', 'full_description',
            'icon_not_started', 'icon_in_progress', 'icon_complete',
            'score_percent', 'score_completed', 'completion_message',
            'required_trophies', 'complete_on_required_satisfied',
            'users'
        ]


class UserTrophyForm(ModelForm):
    class Meta:
        model = models.UserTrophy
        fields = [
            'user', 'trophy',
            'percentage',
            'notified'
        ]
