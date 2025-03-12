from django.db import models

from common.models import BaseModel
from genaibackend.users.models import User


class ConversationManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(status="Deleted")


class Conversation(BaseModel):
    STATUS_ACTIVATE = "Active"
    STATUS_DELETE = "Deleted"
    STATUS_CHOICES = [
        (STATUS_ACTIVATE, "Active"),
        (STATUS_DELETE, "Deleted"),
    ]
    title = models.CharField(max_length=255, blank=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="conversations"
    )
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVATE,
    )
    model_version = models.CharField(max_length=50, default="gpt-4")

    objects = ConversationManager()
    all_objects = models.Manager()

    def __str__(self):
        return f"{self.title} with {self.user.name} (Status: {self.status})"

    def soft_delete(self):
        self.status = self.STATUS_DELETE
        self.save(update_fields=["status"])


class Message(BaseModel):
    SENDER_USER = "user"
    SENDER_AI = "ai"
    SENDER_CHOICE = (
        (SENDER_USER, "user"),
        (SENDER_AI, "ai"),
    )
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.CharField(max_length=20, choices=SENDER_CHOICE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    order = models.PositiveIntegerField(default=0)
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    reply_to = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.sender} - {self.timestamp}: {self.content[:30]}..."

    def save(self, *args, **kwargs):
        if self.order == 0:
            last_order = (
                Message.objects.filter(conversation=self.conversation).aggregate(
                    max_order=models.Max("order")
                )
            )["max_order"] or 0
            self.order = last_order + 1
        super().save(*args, **kwargs)

    def get_status(self):
        if self.sender == "user":
            return "completed"
        if hasattr(self, "ai_response"):
            return self.ai_response.status
        return AIResponse.STATUS_PENDING


class AIResponse(BaseModel):
    STATUS_PENDING = "Pending"
    STATUS_COMPLETED = "Completed"
    STATUS_GENERATING = "Generating"
    STATUS_ERROR = "Error"
    STATUS_CHOICES = [
        (STATUS_COMPLETED, "Completed"),
        (STATUS_GENERATING, "Generating"),
        (STATUS_ERROR, "Error"),
    ]

    message = models.OneToOneField(
        Message, on_delete=models.CASCADE, related_name="ai_response"
    )
    response_content = models.TextField(blank=True)
    status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default=STATUS_GENERATING
    )
    error_message = models.TextField(blank=True, null=True)
    retry_count = models.PositiveIntegerField(default=0)

    def mark_completed(self, response_text):
        self.response_content = response_text
        self.status = self.STATUS_COMPLETED
        self.save(update_fields=["status", "response_content"])

        self.message.content = response_text
        self.message.save(update_fields=["content"])

    def mark_failed(self, error_msg):
        self.retry_count += 1
        if self.retry_count < self.max_retries:
            self.status = self.STATUS_GENERATING
        else:
            self.status = self.STATUS_ERROR
            self.error_message = error_msg
        self.save(update_fields=["status", "error_message", "retry_count"])

    def get_input_token(self):
        """
        TODO get history message in the conversions
        """
        return ""

    def __str__(self):
        return f"Response to Message {self.message.id}: {self.response_content[:50]}"
