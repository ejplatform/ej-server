from rest_framework import serializers

from .models import Job


class JobSerializer(serializers.HyperlinkedModelSerializer):
    argument = serializers.ListField(
        child=serializers.ListField(
            child=serializers.IntegerField()
        )
    )

    class Meta:
        model = Job
        fields = ('id', 'result', 'argument', 'type', 'status',)
