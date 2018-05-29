from django.forms import ModelForm
from ej_conversations.models import Conversation


class ConversationForm(ModelForm):
    class Meta:
        model = Conversation
        fields = ['question', 'title']
