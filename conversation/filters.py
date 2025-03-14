from django_filters import rest_framework as filters

from .models import Conversation, Message


class ConversationFilter(filters.FilterSet):
    status = filters.ChoiceFilter(choices=Conversation.STATUS_CHOICES)
    model_version = filters.CharFilter(
        field_name="model_version", lookup_expr="icontains"
    )

    class Meta:
        model = Conversation
        fields = ["status"]


class MessageFilter(filters.FilterSet):
    conversation_id = filters.NumberFilter(field_name="conversation__id")
    sender = filters.ChoiceFilter(choices=Message.SENDER_CHOICE)
    is_edited = filters.BooleanFilter()
    is_deleted = filters.BooleanFilter()

    class Meta:
        model = Message
        fields = ["conversation_id", "sender", "is_edited", "is_deleted"]
