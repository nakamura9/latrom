from rest_framework import serializers, pagination
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
    messages = serializers.SerializerMethodField('paginated_messages')
    class Meta:
        model = Chat
        fields = "__all__"

    def paginated_messages(self, obj):
        messages = Bubble.objects.filter(chat=obj).order_by('-pk')
        paginator = pagination.PageNumberPagination()
        page = paginator.paginate_queryset(messages, self.context['request'])
        serializer = BubbleReadSerializer(page, many=True, 
            context={'request': self.context['request']}
        )

        return serializer.data


class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Email
        fields = "__all__"

class EmailRetrieveSerializer(EmailSerializer):
    sender = serializers.StringRelatedField(many=False)
    sent_from = serializers.StringRelatedField(many=False)
    to = serializers.StringRelatedField(many=False)
    copy = serializers.StringRelatedField(many=True)
    blind_copy = serializers.StringRelatedField(many=True)


class GroupSerializer(serializers.ModelSerializer):
    messages = serializers.SerializerMethodField('paginated_messages')

    class Meta:
        model = Group
        fields = "__all__"

    def paginated_messages(self, obj):
        messages = Bubble.objects.filter(group=obj)
        paginator = pagination.PageNumberPagination()
        page = paginator.paginate_queryset(messages, self.context['request'])
        serializer = BubbleReadSerializer(page, many=True, 
            context={'request': self.context['request']}
        )
        return serializer.data

class EmailAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailAddress
        fields = "__all__"