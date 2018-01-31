from rest_framework import mixins, viewsets, status
from rest_framework.response import Response

from .models import Job
from .serializers import JobSerializer
from ..conversations.models import Conversation


class JobViewSet(mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    """
    API endpoint that allows the last conversation's job to be viewed.
    """
    serializer_class = JobSerializer
    queryset = Conversation.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
        conversation = get_object_or_404(queryset, pk=self.kwargs['pk'])

        try:
            return conversation.math_jobs.last()
        except Job.DoesNotExist as e:
            return None

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)

        return Response(status=status.HTTP_404_NOT_FOUND)
