from boogie.rest import rest_api
from .models import RasaConversation

#
# Rasa connector
# usage: api/v1/rasa-conversations/integrations?domain=URL
#
@rest_api.list_action("ej_conversations.RasaConversation")
def integrations(request):
    domain = request.GET.get('domain')
    integrations = RasaConversation.objects.filter(domain=domain)
    return integrations