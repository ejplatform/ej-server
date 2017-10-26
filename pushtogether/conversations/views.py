from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import RetrieveModelMixin

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

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


class NextCommentViewSet(RetrieveModelMixin, GenericViewSet):
    serializer_class = CommentSerializer
    queryset = Conversation.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
        current_user = self.request.user
        conversation = get_object_or_404(queryset, pk=self.kwargs['pk'])
        return conversation.get_random_unvoted_comment(current_user)


class CommentReportViewSet(ModelViewSet):
    serializer_class = CommentReportSerializer
    queryset = Comment.objects.all()


class VoteViewSet(ModelViewSet):
    serializer_class = VoteSerializer
    queryset = Vote.objects.all()


class AuthorViewSet(ModelViewSet):
    serializer_class = AuthorSerializer
    queryset = get_user_model().objects.all()
