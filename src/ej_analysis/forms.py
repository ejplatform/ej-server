from django.forms import ModelForm
from .models import OpinionComponent


class OpinionComponentForm(ModelForm):
    class Meta:
        model = OpinionComponent
        fields = ["analytics_property_id", "conversation"]
