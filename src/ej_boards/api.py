from rest_framework import viewsets
from ej.permissions import IsAuthenticatedOnlyGetView
from .models import Board
from .serializers import BoardSerializer


class BoardViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticatedOnlyGetView]
