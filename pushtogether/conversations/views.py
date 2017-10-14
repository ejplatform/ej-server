from rest_framework.viewsets import ModelViewSet

from django.contrib.auth import get_user_model
from .models import Conversation, Comment, Vote
from .serializers import (
    VoteSerializer,
    ConversationSerializer,
    ConversationReportSerializer,
    CommentSerializer,
    CommentReportSerializer,
    AuthorSerializer,
)


class ConversationViewSet(ModelViewSet):
    serializer_class = ConversationSerializer
    queryset = Conversation.objects.all()


class ConversationReportViewSet(ModelViewSet):
    serializer_class = ConversationReportSerializer
    queryset = Conversation.objects.all()


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()


class CommentReportViewSet(ModelViewSet):
    serializer_class = CommentReportSerializer
    queryset = Comment.objects.all()


class VoteViewSet(ModelViewSet):
    serializer_class = VoteSerializer
    queryset = Vote.objects.all()


class AuthorViewSet(ModelViewSet):
    serializer_class = AuthorSerializer
    queryset = get_user_model().objects.all()
