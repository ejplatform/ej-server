from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils.translation import ugettext as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from . import serializers
from .forms import VoteForm
from .mixins import validation_error
from .models import Conversation, Comment, Vote
from .permissions import IsAdminOrReadOnly


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.UserSerializer
    queryset = get_user_model().objects.all()
    lookup_field = 'username'


class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ConversationSerializer
    queryset = Conversation.objects.all()
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['is_promoted', 'category_id']
    lookup_field = 'slug'
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return Conversation.objects.select_related('author', 'category')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True)
    def user_data(self, request, slug):
        conversation = self.get_object()
        return Response(conversation.user_statistics(request.user))

    @action(detail=True)
    def votes(self, request, slug):
        conversation = self.get_object()
        votes = conversation.votes(request.user)
        serializer = serializers.VoteSerializer(votes, many=True,
                                                context={'request': request})
        return Response(serializer.data)

    @action(detail=True)
    def approved_comments(self, request, slug):
        conversation = self.get_object()
        comments = conversation.approved_comments.all()
        serializer = serializers.CommentSerializer(
            comments, many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(detail=True)
    def random_comment(self, request, slug):
        conversation = self.get_object()
        try:
            comment = conversation.next_comment(request.user)
        except Comment.DoesNotExist as msg:
            return Response({
                "message": str(msg),
                "error": True,
            })
        ctx = {'request': request}
        serializer = serializers.CommentSerializer(comment, context=ctx)
        return Response(serializer.data)

    @action(detail=False)
    def random(self, request):
        try:
            conversation = Conversation.objects.random(request.user)
        except Conversation.DoesNotExist as msg:
            return Response({
                'message': _(str(msg)),
                'error': True,
            })
        ctx = {'request': request}
        serializer = serializers.ConversationSerializer(conversation, context=ctx)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CommentSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['status', 'conversation__slug']
    permission_classes = [IsAdminOrReadOnly]
    queryset = Comment.objects.select_related('author', 'conversation')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except PermissionError as err:
            return Response(err.args[0])

    @action(detail=True, methods=['POST'])
    def vote(self, request, pk):
        form = VoteForm(request.POST)
        value = form.get_value()
        comment = self.get_object()

        try:
            vote = comment.vote(author=request.user, choice=value)
            serializer = serializers.VoteSerializer(vote)
            return Response(serializer.data)
        except ValidationError as ex:
            return Response(validation_error(ex))


class VoteViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.VoteSerializer
    queryset = Vote.objects.select_related('comment')
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['comment__conversation__slug']
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return self.queryset.filter(author_id=user.id)
        else:
            return self.queryset.none()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError:
            return Response({
                'message': _('cannot vote twice in the same comment'),
                'error': True,
            })
        except ValidationError as ex:
            return Response(validation_error(ex))
