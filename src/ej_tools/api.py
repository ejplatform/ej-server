from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets

from ej_tools.serializers import RasaConversationSerializer
from .models import RasaConversation


class RasaConversationViewSet(viewsets.ModelViewSet):
    queryset = RasaConversation.objects.all()
    serializer_class = RasaConversationSerializer

    #
    # Rasa connector
    # usage: api/v1/rasa-conversations/integrations?domain=URL
    #
    @action(detail=False)
    def integrations(self, request):
        domain = request.GET.get("domain")
        try:
            integration = RasaConversation.objects.get(domain=domain)
            response = {
                "conversation": {
                    "id": integration.conversation.id,
                    "title": integration.conversation.text,
                    "text": integration.conversation.text,
                },
                "domain": integration.domain,
            }
            return Response(response)
        except RasaConversation.DoesNotExist:
            return Response({}, status=200)
