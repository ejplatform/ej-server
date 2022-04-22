import json
from urllib import request
from datetime import datetime
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from ej.permissions import IsAuthor, IsAuthenticatedOnlyGetView, IsSuperUser, IsAuthenticatedCreationView
from ej.viewsets import RestAPIBaseViewSet
from ej_conversations.models import Conversation, Comment, Vote
from ej_conversations.serializers import ConversationSerializer, CommentSerializer, VoteSerializer
from ej_conversations.models.vote import Vote
from ej_dataviz.utils import votes_as_dataframe


class CommentViewSet(RestAPIBaseViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        if request.user.is_superuser:
            queryset = Comment.objects.all()
        else:
            queryset = Comment.objects.filter(author=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class VoteViewSet(RestAPIBaseViewSet):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    permission_classes = (IsAuthenticatedCreationView | IsAuthor | IsSuperUser | IsAdminUser,)

    def list(self, request):
        if request.user.is_superuser:
            queryset = Vote.objects.all()
        else:
            queryset = Vote.objects.filter(author=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def delete_hook(self, request, instance):
        delete_vote(request, instance)


class ConversationViewSet(RestAPIBaseViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticatedOnlyGetView]

    def list(self, request):
        if request.user.is_superuser:
            queryset = Conversation.objects.all()
        else:
            queryset = Conversation.objects.filter(is_promoted=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, url_path="vote-dataset")
    def vote_dataset(self, request, pk):
        conversation = self.get_object()
        response = conversation.votes.dataframe().to_dict(orient="list")
        return Response(response)

    @action(detail=True)
    def votes(self, request, pk):
        conversation = self.get_object()
        votes = conversation.votes
        if request.GET.get("startDate") and request.GET.get("endDate"):
            start_date = datetime.fromisoformat(request.GET.get("startDate"))
            end_date = datetime.fromisoformat(request.GET.get("endDate"))
            votes = conversation.votes.filter(created__gte=start_date, created__lte=end_date)
        votes_dataframe = votes_as_dataframe(votes)
        votes_dataframe.reset_index(inplace=True)
        votes_dataframe_as_json = votes_dataframe.to_json(orient="records")
        return Response(json.loads(votes_dataframe_as_json))

    @action(detail=True, url_path="user-statistics")
    def user_statistics(self, request, pk):
        conversation = self.get_object()
        response = conversation.statistics_for_user(request.user)
        return Response(response)

    @action(detail=True, url_path="approved-comments")
    def approved_comments(self, request, pk):
        conversation = self.get_object()
        comments = conversation.comments.approved()
        serializer = CommentSerializer(comments, context={"request": request}, many=True)

        return Response(serializer.data)

    @action(detail=True, url_path="user-comments")
    def user_comments(self, request, pk):
        conversation = self.get_object()
        comments = conversation.comments.filter(author=request.user)
        serializer = CommentSerializer(comments, context={"request": request}, many=True)

        return Response(serializer.data)

    @action(detail=True, url_path="user-pending-comments")
    def user_pending_comments(self, request, pk):
        conversation = self.get_object()
        comments = conversation.comments.filter(status="pending", author=request.user)
        serializer = CommentSerializer(comments, context={"request": request}, many=True)

        return Response(serializer.data)

    @action(detail=True, url_path="random-comment")
    def random_comment(self, request, pk):
        conversation = self.get_object()
        comment = conversation.next_comment(request.user)
        serializer = CommentSerializer(comment, context={"request": request})

        return Response(serializer.data)


def delete_vote(request, vote):
    user = request.user

    if user.is_superuser:
        vote.delete()
    elif vote.author_id != user.id:
        raise PermissionError("cannot delete vote from another user")
    else:
        raise PermissionError("user is not allowed to delete votes")
