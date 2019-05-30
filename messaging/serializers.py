from rest_framework import serializers
from .models import *
from common_data.serializers import UserSerializer


class MessageSerializer(serializers.ModelSerializer):
    created_timestamp = serializers.DateTimeField(format="%A, %d %B %Y, %H:%M")
    sender=serializers.StringRelatedField(many=False)
    recipient=serializers.StringRelatedField(many=False)

    class Meta:
        model = Message
        fields = "__all__"


class MessageThreadSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    class Meta:
        model = MessageThread
        fields = "__all__"


class BubbleSerializer(serializers.ModelSerializer):
    created_timestamp = serializers.DateTimeField(format="%A, %d %B %Y, %H:%M", 
        required=False)

    class Meta:
        model = Bubble
        fields = "__all__"

class BubbleReadSerializer(BubbleSerializer):
    sender= UserSerializer(many=False)


class ChatSerializer(serializers.ModelSerializer):
    sender= serializers.StringRelatedField(many=False)
    receiver= serializers.StringRelatedField(many=False)
    messages = BubbleReadSerializer(many=True)
    class Meta:
        model = Chat
        fields = "__all__"

class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Email
        fields = "__all__"

class GroupSerializer(serializers.ModelSerializer):
    messages = BubbleReadSerializer(many=True)

    class Meta:
        model = Group
        fields = "__all__"