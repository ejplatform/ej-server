from random import randint

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import Conversation, Comment, Vote, Category
from . import serializers

import requests
import json


User = get_user_model()


class AuthorAsCurrentUserMixin():

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)


class ConversationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.ConversationSerializer
    queryset = Conversation.objects.all()
    filter_backends = (DjangoFilterBackend, )
    filter_fields = ('promoted', 'category_id', )
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_object(self):
        queryset = self.get_queryset()
        conversation = None
        try:
            conversation = get_object_or_404(queryset, pk=self.kwargs['pk'])
        except ValueError:
            conversation = get_object_or_404(queryset, slug=self.kwargs['pk'])
        return conversation


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.CategorySerializer
    queryset = Category.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_object(self):
        queryset = self.get_queryset()
        category = None
        try:
            category = get_object_or_404(queryset, pk=self.kwargs['pk'])
        except ValueError:
            category = get_object_or_404(queryset, slug=self.kwargs['pk'])
        return category


class ConversationReportViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.ConversationReportSerializer
    queryset = Conversation.objects.all()


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CommentSerializer
    queryset = Comment.objects.all()
    filter_backends = (DjangoFilterBackend, )
    filter_fields = ('conversation__id',)
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = self.request.user
            conversation = Conversation.objects.get(pk=request.data['conversation'])
            response_args = self.process_the_request(user, conversation, serializer)
            return Response(**response_args)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def process_the_request(self, user, conversation, serializer):
        response_args = {}
        previous_conversation_nudge = conversation.get_status(user)
        response_status_code = previous_conversation_nudge.value['status_code']
        response_args = {
            'data': {'nudge': previous_conversation_nudge.value},
            'status': response_status_code,
        }

        if not previous_conversation_nudge.value['errors']:
            self.perform_create(serializer)
            response_args['headers'] = self.get_success_headers(serializer.data)
            self.create
            # we should update the nudge status before respond the request
            # because the creation of a new comment may alter the status
            new_nudge_status = conversation.get_status(user).value
            response_args['data']['nudge'] = new_nudge_status
            response_args['data'].update(serializer.data)

        return response_args

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    # def perform_update(self, serializer):
    #     # If there is a polis instance set, update its moderation data for the current comment
    #     if settings.POLIS_BASE_URL and settings.POLIS_API_KEY:
    #         conversation_id = self.request.data['conversation']
    #         conversation_slug = Conversation.objects.get(id=conversation_id).polis_slug
    #         polis_id = Comment.objects.get(id=self.request.data['id']).polis_id

    #         # Make the POST call to the polis instance now
    #         payload = {
    #             'polisApiKey': settings.POLIS_API_KEY,
    #             'conversation_id': str(conversation_slug),
    #             'tid': polis_id,
    #             'mod': self.get_polis_moderation_value(self.request.data['approval']),
    #             'active': True,
    #             'is_meta': False,
    #             'velocity': 1
    #         }
    #         response = requests.put(settings.POLIS_BASE_URL + '/api/v3/comments',
    #             headers={'content-type': 'application/json; charset=UTF-8'}, data=json.dumps(payload), timeout=10)

    #         # If the request returned a non 2xx status code, raise an exception now
    #         response.raise_for_status()

    #     serializer.save()

    # def get_polis_moderation_value(self, moderation):
    #     """
    #     Helper function to translate moderation values from EJ to polis standards
    #     """
    #     switcher = {
    #         'UNMODERATED': 0,
    #         'REJECTED': -1,
    #         'APPROVED': 1,
    #     }
    #     return switcher.get(moderation)

    def get_queryset(self):
        user = self.request.user
        queryset = super(CommentViewSet, self).get_queryset()

        # TODO: uncomment this when
        # if user.is_authenticated and not user.is_superuser:
        #     queryset = queryset.filter(author=user)
        return queryset

    def get_serializer_class(self):
        if self.action in ('update', 'partial_update'):
            return serializers.CommentApprovalSerializer
        else:
            return self.serializer_class

    def get_permissions(self):
        if self.action in ('update', 'partial_update'):
            self.permission_classes = [permissions.IsAdminUser, ]
        return super(self.__class__, self).get_permissions()


class NextCommentViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = serializers.CommentSerializer
    queryset = Conversation.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
        current_user = self.request.user
        conversation = get_object_or_404(queryset, pk=self.kwargs['pk'])

        try:
            return conversation.get_next_comment(current_user)
        except Comment.DoesNotExist as e:
            return None

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)

        return Response(status=status.HTTP_404_NOT_FOUND)


class RandomConversationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.ConversationSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Conversation.objects.all()

    def retrieve(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        how_many_conversations = queryset.count()
        random_conversation = queryset.all()[randint(0, how_many_conversations - 1)]
        serializer = self.get_serializer(random_conversation)
        return Response(serializer.data)

    def get_object(self):
        queryset = self.get_queryset()
        conversation = get_object_or_404(queryset)
        return conversation


class CommentReportViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.CommentReportSerializer
    queryset = Comment.objects.all().order_by('-pk')
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,)
    filter_fields = ('conversation__id', 'approval',)
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


class ClustersViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.ConversationJobSerializer
    queryset = Conversation.objects.all()


class VoteViewSet(AuthorAsCurrentUserMixin, viewsets.ModelViewSet):
    serializer_class = serializers.VoteSerializer
    queryset = Vote.objects.all()


class AuthorViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.AuthorSerializer
    queryset = User.objects.all()
