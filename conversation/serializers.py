from rest_framework import serializers

from .models import AIResponse, Conversation, Message


class AIResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIResponse
        fields = ["status", "response_content", "error_message"]


class MessageSerializer(serializers.ModelSerializer):
    ai_response = AIResponseSerializer(read_only=True)
    status = serializers.CharField(source="get_status", read_only=True)

    class Meta:
        model = Message
        fields = [
            "id",
            "sender",
            "content",
            "timestamp",
            "order",
            "is_edited",
            "is_deleted",
            "reply_to",
            "ai_response",
            "status",
        ]


class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = [
            "id",
            "title",
            "user",
            "status",
            "model_version",
        ]
        read_only_fields = [
            "id",
            "user",
            "created_at",
            "updated_at",
        ]


class ConversationDetailSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = [
            "id",
            "title",
            "user",
            "status",
            "model_version",
            "created_at",
            "updated_at",
            "messages",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "messages"]


class AddMessageSerializer(serializers.Serializer):
    content = serializers.CharField(
        required=True, max_length=1000, help_text="The content of the message to add."
    )


class StartConversationSerializer(serializers.Serializer):
    content = serializers.CharField(
        required=True, max_length=1000, help_text="The content of the message to add."
    )
    model_version = serializers.CharField(help_text="user model", allow_blank=True)
