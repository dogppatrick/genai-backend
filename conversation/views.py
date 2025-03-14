from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.utils import set_default_log
from genaibackend.users.authentication import JWTAuthentication

from .filters import ConversationFilter, MessageFilter
from .models import Conversation, Message
from .serializers import (AddMessageSerializer, ConversationDetailSerializer,
                          ConversationSerializer, MessageSerializer,
                          StartConversationSerializer)
from .tasks import auto_title, response_ai

logger = set_default_log()


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ConversationFilter

    def get_queryset(self):
        user = self.request.user
        queryset = (
            Conversation.objects.filter(user=user)
            .select_related("user")
            .prefetch_related("messages")
        )

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
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

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

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)


class MessageViewSet(
    mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet
):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = MessageFilter

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


class StartConversationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=StartConversationSerializer,
        responses={201: ConversationSerializer},
    )
    def post(self, request, pk=None):
        if "content" not in request.data:
            return Response(
                {"error": "Message content is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if "model_version" in request.data:
            new_conversation = Conversation.objects.create(
                user=request.user, model_version=request.data["model_version"]
            )
        else:
            new_conversation = Conversation.objects.create(user=request.user)

        with transaction.atomic():
            user_ask_message = Message.objects.create(
                conversation=new_conversation,
                sender=Message.SENDER_USER,
                content=request.data["content"],
            )
            ai_response_message = Message.objects.create(
                conversation=new_conversation,
                sender=Message.SENDER_AI,
            )
            logger.info(f"message{user_ask_message.id} create")
        response_ai.apply_async(args=[ai_response_message.id], countdown=2)
        auto_title.apply_async(args=[new_conversation.id], countdown=2)

        return Response(
            ConversationSerializer(new_conversation).data,
            status=status.HTTP_201_CREATED,
        )


class AddMessageAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=AddMessageSerializer,
        responses={
            201: MessageSerializer,
            404: OpenApiResponse(description="Conversation not found"),
        },
    )
    def post(self, request, pk=None):
        """
        Add a new message to a conversation.
        """
        try:
            conversation = Conversation.objects.get(id=pk, user=request.user)
        except Conversation.DoesNotExist:
            return Response(
                {"error": "Conversation not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        if "content" not in request.data:
            return Response(
                {"error": "Message content is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        with transaction.atomic():
            user_ask_message = Message.objects.create(
                conversation=conversation,
                sender=Message.SENDER_USER,
                content=request.data["content"],
            )
            ai_response_message = Message.objects.create(
                conversation=conversation,
                sender=Message.SENDER_AI,
            )
            logger.info(f"message{user_ask_message.id} create")
        response_ai.apply_async(args=[ai_response_message.id], countdown=2)

        return Response(
            MessageSerializer(user_ask_message).data, status=status.HTTP_201_CREATED
        )
