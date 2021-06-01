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

@rest_api.detail_action("ej_conversations.RasaConversation")
def delete_connection(request, connection):
    user = request.user
    if user.is_superuser or connection.conversation.author.id == user.id:
        connection.delete()
    elif connection.conversation.author.id != user.id:
        raise PermissionError("cannot delete connection from another user")
    else:
        raise PermissionError("user is not allowed to delete connections")
