from rest_framework import serializers
from rest_framework.reverse import reverse
from ej_tools.models import ConversationMautic, MauticClient
from ej_users.models import SignatureFactory
from ej.serializers import BaseApiSerializer
from .models import Conversation, Comment, Vote
from ej_users.models import User
from ej_boards.models import Board


class ConversationSerializer(BaseApiSerializer):
    author = serializers.SlugRelatedField(read_only=True, slug_field="email")
    board = serializers.SlugRelatedField(read_only=True, slug_field="title")
    links = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "links",
            "title",
            "text",
            "author",
            "slug",
            "created",
            "id",
            "board",
            "statistics",
        ]

    def get_links(self, obj):
        links = {
            "self": reverse("v1-conversations-detail", args=[obj.id], request=self.context["request"]),
            "vote-dataset": reverse(
                "v1-conversations-vote-dataset", args=[obj.id], request=self.context["request"]
            ),
            "votes": reverse("v1-conversations-votes", args=[obj.id], request=self.context["request"]),
            "user-statistics": reverse(
                "v1-conversations-user-statistics", args=[obj.id], request=self.context["request"]
            ),
            "approved-comments": reverse(
                "v1-conversations-approved-comments", args=[obj.id], request=self.context["request"]
            ),
            "user-comments": reverse(
                "v1-conversations-user-comments", args=[obj.id], request=self.context["request"]
            ),
            "user-pending-comments": reverse(
                "v1-conversations-user-pending-comments", args=[obj.id], request=self.context["request"]
            ),
            "random-comment": reverse(
                "v1-conversations-random-comment", args=[obj.id], request=self.context["request"]
            ),
        }
        links["clusterization"] = (
            reverse(
                "v1-clusterizations-detail", args=[obj.clusterization.id], request=self.context["request"]
            )
            if hasattr(obj, "clusterization")
            else None
        )
        links["author"] = (
            reverse("v1-users-detail", args=[obj.author.id], request=self.context["request"])
            if hasattr(obj, "author")
            else None
        )
        links["board"] = (
            reverse("v1-boards-detail", args=[obj.board.id], request=self.context["request"])
            if hasattr(obj, "board")
            else None
        )
        return links

    def get_instance(self, request, validated_data):
        author = User.objects.get(id=request.data.get("author"))  # TODO: pegar o request.user?
        board = Board.objects.get(id=request.data.get("board"))
        validated_data["author"] = author
        validated_data["board"] = board
        return Conversation(**validated_data)


class CommentSerializer(BaseApiSerializer):
    links = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ["links", "content", "status", "created", "rejection_reason", "rejection_reason_text"]

    def get_links(self, obj):
        return {
            "self": reverse("v1-comments-detail", args=[obj.id], request=self.context["request"]),
        }

    def get_instance(self, request, validated_data):
        conversation_id = request.data.get("conversation")
        conversation = Conversation.objects.get(id=conversation_id)
        validated_data["author"] = request.user
        validated_data["conversation"] = conversation
        validated_data["status"] = "pending"
        return Comment(**validated_data)

    def save_hook(self, request, comment):
        try:
            comment.save()
            return comment
        except Exception:
            raise PermissionError("could not create comment")


class VoteSerializer(BaseApiSerializer):
    links = serializers.SerializerMethodField()
    comment = serializers.SlugRelatedField(read_only=True, slug_field="content")

    class Meta:
        model = Vote
        fields = ["links", "comment", "choice", "created", "channel", "analytics_utm"]

    def get_links(self, obj):
        return {
            "self": reverse("v1-votes-detail", args=[obj.id], request=self.context["request"]),
            "comment": reverse(
                "v1-comments-detail", args=[obj.comment.id], request=self.context["request"]
            ),
        }

    def get_instance(self, request, validated_data):
        comment_id = request.data.get("comment")
        comment = Comment.objects.get(id=comment_id)
        validated_data["comment"] = comment
        return Vote(**validated_data)

    def save_hook(self, request, vote):
        user = request.user
        create_mautic_contact_from_author(request, vote)

        user_signature = SignatureFactory.get_user_signature(user)
        if user_signature.can_vote():
            try:
                skipped_vote = Vote.objects.get(comment=vote.comment, choice=0, author=user)
                skipped_vote.choice = vote.choice
                skipped_vote.analytics_utm = vote.analytics_utm
                skipped_vote.save()
                return skipped_vote
            except Exception as e:
                pass
            if vote.id is None:
                vote.author = user
                vote.save()
            elif vote.author != user:
                raise PermissionError("cannot update vote of a different user")
            else:
                vote.save(update_fields=["choice", "analytics_utm"])
            return vote
        else:
            raise PermissionError("vote limit reached")


def create_mautic_contact_from_author(request, vote):
    conversation = vote.comment.conversation
    try:
        conversation_mautic = ConversationMautic.objects.get(conversation=conversation)
        mautic_client = MauticClient(conversation_mautic)
        create_contact_from_author = mautic_client.create_contact(request, vote)
        return create_contact_from_author
    except:
        pass
