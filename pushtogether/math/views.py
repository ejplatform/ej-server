from rest_framework import mixins, viewsets, status
from rest_framework.response import Response

from .models import Job
from .serializers import JobSerializer


class JobViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = JobSerializer
    queryset = Job.objects.all()
