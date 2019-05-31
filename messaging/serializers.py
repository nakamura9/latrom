from rest_framework import serializers
from .models import *
from common_data.serializers import UserSerializer
from rest_framework.parsers import FormParser, MultiPartParser

class BubbleSerializer(serializers.ModelSerializer):
    parser_classes = (FormParser, MultiPartParser)
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

class EmailRetrieveSerializer(EmailSerializer):
    sender = serializers.StringRelatedField(many=False)
    to = serializers.StringRelatedField(many=False)

class GroupSerializer(serializers.ModelSerializer):
    messages = BubbleReadSerializer(many=True)

    class Meta:
        model = Group
        fields = "__all__"