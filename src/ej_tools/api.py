from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from ej_conversations.models import Conversation
from ej_tools.serializers import RasaConversationSerializer
from .models import RasaConversation


class RasaConversationViewSet(viewsets.ModelViewSet):
    queryset = RasaConversation.objects.all()
    serializer_class = RasaConversationSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        if request.user.is_superuser:
            queryset = RasaConversation.objects.all()
        else:
            conversation = Conversation.objects.filter(author=request.user)
            queryset = RasaConversation.objects.filter(conversation__in=conversation)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    #
    # Rasa connector
    # usage: api/v1/rasa-conversations/integrations?domain=URL
    #
    @action(detail=False, permission_classes=[AllowAny])
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
