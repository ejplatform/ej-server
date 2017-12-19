from pprint import pprint

from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.decorators import detail_route, list_route
from rest_framework import permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import Conversation, Comment, Vote
from .serializers import (
    VoteSerializer,
    ConversationSerializer,
    ConversationReportSerializer,
    CommentSerializer,
    CommentApprovalSerializer,
    CommentReportSerializer,
    AuthorSerializer,
)


User = get_user_model()


class AuthorAsCurrentUserMixin():

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)


class ConversationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ConversationSerializer
    queryset = Conversation.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_object(self):
        queryset = self.get_queryset()
        conversation = None
        try:
            conversation = get_object_or_404(queryset, pk=self.kwargs['pk'])
        except ValueError:
            conversation = get_object_or_404(queryset, slug=self.kwargs['pk'])
        return conversation


class ConversationReportViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ConversationReportSerializer
    queryset = Conversation.objects.all()


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    filter_backends = (DjangoFilterBackend, )
    filter_fields = ('polis_id', 'conversation__id',)
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            conversation = Conversation.objects.get(pk=request.data['conversation'])
            conversation_nudge = conversation.get_nudge_status(self.request.user)
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

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        user = self.request.user
        queryset = super(CommentViewSet, self).get_queryset()

        # TODO: uncomment this when
        # if user.is_authenticated and not user.is_superuser:
        #     queryset = queryset.filter(author=user)
        return queryset

    def get_serializer_class(self):
        if self.action in ('update', 'partial_update'):
            return CommentApprovalSerializer
        else:
            return self.serializer_class

    def get_permissions(self):
        if self.action in ('update', 'partial_update'):
            self.permission_classes = [permissions.IsAdminUser, ]
        return super(self.__class__, self).get_permissions()


class NextCommentViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = CommentSerializer
    queryset = Conversation.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
        current_user = self.request.user
        conversation = get_object_or_404(queryset, pk=self.kwargs['pk'])

        try:
            return conversation.get_random_unvoted_comment(current_user)
        except Comment.DoesNotExist as e:
            return None

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)

        return Response(status=status.HTTP_404_NOT_FOUND)


class CommentReportViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CommentReportSerializer
    queryset = Comment.objects.all()
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,)
    filter_fields = ('polis_id', 'conversation__id', 'conversation__polis_slug', 'approval',)
    search_fields = ('content', 'author__name')
    ordering_fields = ('created_at', )
    pagination_class = PageNumberPagination
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        queryset = super(CommentReportViewSet, self).get_queryset()
        if user.is_authenticated and not user.is_superuser:
            queryset = queryset.filter(author=user)
        return queryset


class VoteViewSet(AuthorAsCurrentUserMixin, viewsets.ModelViewSet):
    serializer_class = VoteSerializer
    queryset = Vote.objects.all()


class AuthorViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AuthorSerializer
    queryset = User.objects.all()
