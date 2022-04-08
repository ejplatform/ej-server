from .models import Board
from .serializers import BoardSerializer
from rest_framework import viewsets


class BoardViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
