from django.contrib import admin

from .models import AIResponse, Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 1


class AIResponseInline(admin.TabularInline):
    model = AIResponse
    extra = 1


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "status", "model_version")
    list_filter = ("status", "model_version")
    search_fields = ("title", "user__username")
    ordering = ("-created_at",)
    inlines = [MessageInline]

    def get_queryset(self, request):
        return Conversation.all_objects.all()


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "conversation",
        "sender",
        "content_preview",
        "timestamp",
        "order",
        "is_edited",
        "is_deleted",
    )
    list_filter = ("sender", "is_edited", "is_deleted")
    search_fields = ("conversation__title", "content")
    ordering = ("conversation", "order")

    def content_preview(self, obj):
        return f"{obj.content[:50]}..."

    content_preview.short_description = "Content Preview"


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
