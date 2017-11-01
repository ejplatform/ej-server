from pprint import pprint

from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet, ReadOnlyModelViewSet
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.decorators import detail_route, list_route
from django_filters.rest_framework import DjangoFilterBackend

from .models import Conversation, Comment, Vote
from .serializers import (
    VoteSerializer,
    ConversationSerializer,
    ConversationReportSerializer,
    CommentSerializer,
    CommentReportSerializer,
    AuthorSerializer,
)


User = get_user_model()

class AuthorAsCurrentUserMixin():

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)


class ConversationViewSet(ModelViewSet):
    serializer_class = ConversationSerializer
    queryset = Conversation.objects.all()


class ConversationReportViewSet(ModelViewSet):
    serializer_class = ConversationReportSerializer
    queryset = Conversation.objects.all()


class CommentViewSet(AuthorAsCurrentUserMixin, ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('polis_id',)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            conversation = Conversation.objects.get(pk=request.data['conversation'])
            user  = User.objects.get(pk=request.data['author'])
            conversation_nudge = conversation.get_nudge_status(user)
            response_data = {"nudge": conversation_nudge.value}
            if conversation_nudge.value['errors']:
                return Response(response_data, status=conversation_nudge.value['status_code'])
            else:
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                self.create
                response_data.update(serializer.data)
                return Response(response_data, headers=headers,
                                status=conversation_nudge.value['status_code'])
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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


class VoteViewSet(AuthorAsCurrentUserMixin, ModelViewSet):
    serializer_class = VoteSerializer
    queryset = Vote.objects.all()


class AuthorViewSet(ReadOnlyModelViewSet):
    serializer_class = AuthorSerializer
    queryset = User.objects.all()
