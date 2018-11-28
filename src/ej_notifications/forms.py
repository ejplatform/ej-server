from django.forms import ModelForm

from . import models


class NotificationConfigForm(ModelForm):

    class Meta:
        model = models.NotificationConfig
        fields = ['notification_option']
