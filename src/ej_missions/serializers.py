from . import models
from ej_users.models import User
from rest_framework import serializers
from ej_trophies.models.user_trophy import UserTrophy
import datetime


class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('display_name', 'id', 'email', 'name')

class CommentSerializer(serializers.ModelSerializer):
    user = OwnerSerializer(read_only=True)

    class Meta:
        model = models.Comment
        fields = ('user', 'comment')

class MissionSerializer(serializers.ModelSerializer):
    owner = OwnerSerializer(read_only=True)
    comment_set = CommentSerializer(many=True)
    remainig_days = serializers.SerializerMethodField()

    def get_remainig_days(self, obj):
        deadline_in_days = (obj.deadline - datetime.date.today()).days

        if(deadline_in_days < 0):
            return "missão encerrada"
        if(deadline_in_days == 0):
            return "encerra hoje"
        if(deadline_in_days == 1):
            return "encerra amanhã"

        return "{} dias restantes".format(deadline_in_days);

    class Meta:
        model = models.Mission
        fields = ('id', 'title', 'description', 'users', 'image', 'youtubeVideo', 'audio', 'owner', 'remainig_days', 'deadline', 'comment_set', 'reward')

class MissionInboxSerializer(MissionSerializer):

    blocked = serializers.SerializerMethodField()

    class Meta:
        model = models.Mission
        fields='__all__'

    def get_blocked(self, obj):

        def filter_trophies(user_trophy):
            return (user_trophy.trophy.key == req.key and\
                user_trophy.percentage == 100)

        required_trophies = obj.trophy.required_trophies.all()
        user_trophies = UserTrophy.objects.filter(percentage=100,
                                                  user_id= self.context['uid'])
        if (len(required_trophies) == 0):
            return False

        filtered_trophies = []
        for req in required_trophies:
            filtered = list(filter(filter_trophies, list(user_trophies)))
            if len(filtered) > 0:
                filtered_trophies.append(filtered)
        if (len(filtered_trophies) == len(required_trophies)):
            return False

        return True

class MissionReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Receipt
        fields = ('id',
                  'userName',
                  'userEmail',
                  'status',
                  'description',
                  'receiptFile',
                  'user')

