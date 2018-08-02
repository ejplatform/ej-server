from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.request import Request
import json
from django import forms
from django.http import QueryDict

from . import serializers
from . import models
from ej_users.models import User, UserConversations
from ej_trophies.models.user_trophy import UserTrophy


class MissionViewSet(viewsets.ViewSet):

    def list(self, request):
        queryset = models.Mission.objects.all().order_by("-created_at")
        serializer = serializers.MissionSerializer(queryset, many=True)
        return Response(serializer.data)

    def inbox(self, request, pk):
        queryset = models.Mission.objects.all().order_by("-created_at")
        serializer = serializers.MissionInboxSerializer(queryset,
                                                        many=True,
                                                        context={'uid': pk})
        return Response(serializer.data)

    def accepted_missions(self, request, pk):
        queryset = models.Mission.objects.filter(users=pk).order_by("-created_at")
        serializer = serializers.MissionSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk):
        queryset = models.Mission.objects.get(id=pk)
        serializer = serializers.MissionSerializer(queryset)
        return Response(serializer.data)

    def create(self, request):
        data = request.POST
        owner = User.objects.get(id=data["owner"])
        mission = models.Mission(owner=owner,
                                 title=data["title"],
                                 description=data["description"])

        mission.save()
        try:
            mission.image=request.FILES["coverFile"];
        except KeyError:
            print('no coverFile submitted')
        try:
            mission.audio=request.FILES["audioFile"];
        except KeyError:
            print('no audioFile submitted')
        try:
            mission.youtubeVideo=data["videoLink"];
        except KeyError:
            print('no videoLink submitted')

        mission.save()
        serializer = serializers.MissionSerializer(mission)
        return Response(serializer.data)

    def accept(self, request):
        data = json.loads(request.body.decode("utf8"))
        user = User.objects.filter(id=data["user_id"])[0]
        mission = models.Mission.objects.filter(id=data["id"])[0]
        mission.users.add(user)
        user_trophy = UserTrophy(user=user, trophy=mission.trophy)
        user_trophy.save()
        serializer = serializers.MissionSerializer(mission)
        return Response(serializer.data)

    def receipt(self, request, pk):
        data = request.POST
        mission = models.Mission.objects.filter(id=pk)[0]
        user = User.objects.filter(id=data["uid"])[0]
        receipt = models.Receipt(userName=data["userName"],
                                 userEmail=data["userEmail"],
                                 status=data["status"],
                                 description=data["description"])
        try:
            receipt.receiptFile=request.FILES["receiptFile"];
        except KeyError:
            print('no receiptFile submitted')

        receipt.user = user
        receipt.mission = mission
        receipt.save()
        # With a many to one relation, add receipt directly on mission.
        mission.receipt_set.add(receipt)
        serializer = serializers.MissionSerializer(mission)
        return Response(serializer.data)

    def update_receipt(self, request, pk):
        data = json.loads(request.body.decode("utf8"))
        receipt = models.Receipt.objects.filter(id=pk)[0]
        receipt.status = data["status"]
        receipt.save()
        serializer = serializers.MissionReceiptSerializer(receipt)
        return Response(serializer.data)

    def receipts(self, request, pk):
        queryset = models.Mission.objects.filter(id=pk)[0].receipt_set.all()
        serializer = serializers.MissionReceiptSerializer(queryset, many=True)
        return Response(serializer.data)

    def user_status(self, request, mid, uid):
        mission = models.Mission.objects.filter(id=mid)[0]
        user = models.User.objects.filter(id=uid)[0]
        status = {"status": "new"}
        if (len(mission.users.all()) > 0 and user in mission.users.all()):
            status["status"] = "started";

        for receipt in mission.receipt_set.all():
            if (uid == str(receipt.user.id)):
             status["status"] = receipt.status

        if (mission.get_blocked(mission, user)):
            status["status"] = "blocked"

        return Response(status)

    def statistics(self, request, pk):

        statistics = {}
        statistics["realized"] = 0
        statistics["pending"] = 0
        mission = models.Mission.objects.filter(id=pk)[0]
        statistics["accepted"] = len(mission.users.all())

        for receipt in mission.receipt_set.all():
            if (receipt.status == "realized"):
             statistics["realized"] += 1
            if (receipt.status == "pending"):
             statistics["pending"] += 1

        return Response(statistics)

    def comments(self, request, pk):
        mission = models.Mission.objects.get(id=pk)
        queryset = mission.comment_set.all()
        serializer = serializers.CommentSerializer(queryset, many=True)
        return Response(serializer.data)


    def add_comment(self, request, pk):
        mission = models.Mission.objects.get(id=pk)
        data = json.loads(request.body.decode("utf8"))
        user = User.objects.get(id=data["user_id"])
        comment = models.Comment(mission=mission,
                                 user=user,
                                 comment=data["comment"])
        comment.save()
        mission.comment_set.add(comment)
        serializer = serializers.CommentSerializer(comment)
        return Response(serializer.data)

    def conversation_comments(self, request, mid, cid, uid):
        mission = models.Mission.objects.get(pk=mid)
        conversation = mission.conversations.get(pk=cid)
        comments = conversation.comments.exclude(votes__author=uid)[:3]
        serializer = serializers.ConversationCommentSerializer(comments, many=True)
        return Response(serializer.data)

    def next_conversation(self, request, mid, uid):
        mission = models.Mission.objects.get(pk=mid)
        if (len(mission.conversations.all()) == 0):
            return Response({"comments_count": 0})
        user_conversations = UserConversations.objects.filter(user=uid)
        if (len(user_conversations) == 0):
            mission_conversation = mission.conversations.all().first()
            user_conversation = UserConversations(user=User.objects.get(pk=uid),
                                                  last_viewed_conversation=0)
            user_conversation.save()
            user_conversation.conversations.add(mission_conversation)
            user_conversation.save()
            comments_count = len(mission_conversation.comments.exclude(votes__author=uid))
            return Response({"cid": mission_conversation.id,
                             "comments_count": comments_count})
        else:
            user_conversations = user_conversations[0]
            last_conversation_idx = user_conversations.last_viewed_conversation
            last_conversation = user_conversations.conversations.all()[last_conversation_idx]
            first_conversation = user_conversations.conversations.all().first()
            mission_conversations = mission.conversations.all()

            if(last_conversation_idx == len(mission.conversations.all()) - 1):
                user_conversations.last_viewed_conversation = 0
                user_conversations.save()
                comments_count = len(first_conversation.comments.exclude(votes__author=uid))
                return Response({"cid": first_conversation.id,
                                 "comments_count": comments_count })

            next_conversation = None
            for m in mission_conversations:
                if m.id > last_conversation.id:
                    next_conversation = m
                    break

            if (next_conversation):
                user_conversations.conversations.add(next_conversation)
                user_conversations.last_viewed_conversation += 1
                user_conversations.save()
                comments_count = len(next_conversation.comments.exclude(votes__author=uid))
                return Response({"cid": next_conversation.id,
                                "comments_count": comments_count})
            return Response({})
