from django.contrib import admin

from .models import AIResponse, Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "user", "status", "model_version")
    list_filter = ("status", "model_version")
    search_fields = ("title", "user__username")
    ordering = ("-created_at",)
    inlines = [MessageInline]

    def get_queryset(self, request):
        return Conversation.all_objects.all()


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "conversation",
        "sender",
        "content_preview",
        "get_status",
        "timestamp",
    )
    list_filter = ("sender", "is_edited", "is_deleted")
    search_fields = ("conversation__title", "content")
    ordering = ("conversation", "order")

    def content_preview(self, obj):
        return f"{obj.content[:50]}..."

    def get_status(self, obj: Message):
        return obj.get_status()

    content_preview.short_description = "Content Preview"
    get_status.short_description = "status"


@admin.register(AIResponse)
class AIResponseAdmin(admin.ModelAdmin):
    list_display = (
        "message",
        "status",
        "response_content_preview",
        "retry_count",
        "error_message",
    )
    list_filter = ("status",)
    search_fields = ("message__content", "response_content")
    ordering = ("-created_at",)

    def response_content_preview(self, obj):
        return f"{obj.response_content[:50]}..."

    response_content_preview.short_description = "Response Preview"
