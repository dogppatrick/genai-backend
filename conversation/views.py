from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AIResponse, Conversation, Message
from .serializers import (AddMessageSerializer, ConversationDetailSerializer,
                          ConversationSerializer, MessageSerializer)
from .tasks import response_ai


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        queryset = Conversation.objects.filter(user=user)

        search = self.request.query_params.get("search", None)
        if search:
            queryset = queryset.filter(title__icontains=search)

        return queryset.order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ConversationDetailSerializer
        return ConversationSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()

        data["user"] = request.user.id

        # Extract first message if provided
        first_message = data.pop("message", None)

        # Create conversation
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        conversation = serializer.save()

        # Create first message if provided
        if first_message:
            message = Message.objects.create(
                conversation=conversation,
                sender=Message.SENDER_USER,
                content=first_message,
            )

            # Create AI response record
            ai_response = AIResponse.objects.create(
                message=message, status=AIResponse.STATUS_GENERATING
            )

            # Trigger Celery task
            response_ai.delay(message.id)

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        # Only allow updating title and status
        data = {
            "title": request.data.get("title", instance.title),
            "status": request.data.get("status", instance.status),
        }

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)


class MessageViewSet(
    mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet
):
    serializer_class = MessageSerializer

    def get_queryset(self):
        return Message.objects.filter(conversation__user=self.request.user)

    @action(detail=True, methods=["patch"])
    def mark_deleted(self, request, pk=None):
        message = self.get_object()
        message.is_deleted = True
        message.save(update_fields=["is_deleted"])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["patch"])
    def edit_message(self, request, pk=None):
        message = self.get_object()

        # Only allow editing user messages that haven't been deleted
        if message.sender != Message.SENDER_USER or message.is_deleted:
            return Response(
                {"error": "Cannot edit this message"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if "content" not in request.data:
            return Response(
                {"error": "New content is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        message.content = request.data["content"]
        message.is_edited = True
        message.save(update_fields=["content", "is_edited"])

        serializer = self.get_serializer(message)
        return Response(serializer.data)


class AddMessageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk=None):
        """
        Add a new message to a conversation.
        """
        conversation = Conversation.objects.get(id=pk, user=request.user)
        if "content" not in request.data:
            return Response(
                {"error": "Message content is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # # Create the new message
        message = Message.objects.create(
            conversation=conversation,
            sender=Message.SENDER_USER,
            content=request.data["content"],
        )

        # Create AI response record
        ai_response = AIResponse.objects.create(
            message=message, status=AIResponse.STATUS_GENERATING
        )

        # Trigger Celery task for AI response
        # response_ai.delay(message.id)

        return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)


class SoftDeleteConversationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk=None):
        """
        Soft delete a conversation by changing its status to 'Deleted'.
        """
        conversation = Conversation.all_objects.get(id=pk, user=request.user)
        conversation.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
