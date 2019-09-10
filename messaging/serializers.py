from rest_framework import serializers, pagination
from .models import *
from common_data.serializers import UserSerializer
from rest_framework.parsers import FormParser, MultiPartParser
import messaging
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
        paginator = messaging.views.api.MessagingPaginator()
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
    body = serializers.SerializerMethodField('get_body')

    def get_body(self, obj):
        body = obj.read_body()
        return body
        
class GroupSerializer(serializers.ModelSerializer):
    messages = serializers.SerializerMethodField('paginated_messages')
    participants = UserSerializer(many=True)
    
    class Meta:
        model = Group
        fields = "__all__"

    def paginated_messages(self, obj):
        messages = Bubble.objects.filter(group=obj)
        paginator = messaging.views.api.MessagingPaginator()
        page = paginator.paginate_queryset(messages, self.context['request'])
        serializer = BubbleReadSerializer(page, many=True, 
            context={'request': self.context['request']}
        )
        return serializer.data

class EmailAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailAddress
        fields = "__all__"

class EmailFolderRetrieveSerializer(serializers.ModelSerializer):
    #emails = serializers.SerializerMethodField('get_emails')
    
    class Meta:
        model = EmailFolder
        fields = "__all__"

class EmailFolderSerializer(serializers.ModelSerializer):
    emails = serializers.SerializerMethodField('get_emails')
    
    class Meta:
        model = EmailFolder
        fields = "__all__"

    def get_emails(self, obj):
        return EmailRetrieveSerializer(obj.emails, many=True).data


class UserProfileSerializer(serializers.ModelSerializer):
    folders = serializers.SerializerMethodField('get_folders')
    class Meta:
        model = UserProfile
        fields = "__all__"

    def get_folders(self, obj):
        return EmailFolderRetrieveSerializer(obj.folders, many=True).data