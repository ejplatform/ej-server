from pprint import pprint

from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.decorators import detail_route, list_route

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

class ConversationViewSet(ModelViewSet):
    serializer_class = ConversationSerializer
    queryset = Conversation.objects.all()


class ConversationReportViewSet(ModelViewSet):
    serializer_class = ConversationReportSerializer
    queryset = Conversation.objects.all()


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            conversation = Conversation.objects.get(pk=request.data['conversation'])
            user  = User.objects.get(pk=request.data['author'])
            if (not conversation.can_user_post_comment(user)):
                return Response({"Error":_("Sorry, you can't write too many comments")},
                    status=status.HTTP_429_TOO_MANY_REQUESTS)
            else:
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                self.create
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
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


class VoteViewSet(ModelViewSet):
    serializer_class = VoteSerializer
    queryset = Vote.objects.all()


class AuthorViewSet(ModelViewSet):
    serializer_class = AuthorSerializer
    queryset = User.objects.all()
