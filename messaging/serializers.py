from rest_framework import serializers
from .models import *


class MessageSerializer(serializers.ModelSerializer):
    thread_pk = serializers.SerializerMethodField()
    created_timestamp = serializers.DateTimeField(format="%A, %d %B %Y, %H:%M")
    sender=serializers.StringRelatedField(many=False)
    recipient=serializers.StringRelatedField(many=False)

    class Meta:
        model = Message
        fields = "__all__"

    def get_thread_pk(self, obj):
        return obj.thread_pk

class MessageThreadSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True)
    class Meta:
        model = MessageThread
        fields = "__all__"