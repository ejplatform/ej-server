from rest_framework import viewsets

from .models import Job
from .serializers import JobSerializer


class JobViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = JobSerializer
    queryset = Job.objects.order_by('id')
