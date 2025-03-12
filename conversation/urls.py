from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (AddMessageAPIView, ConversationViewSet, MessageViewSet,
                    SoftDeleteConversationAPIView)

router = DefaultRouter()
router.register(r"conversations", ConversationViewSet, basename="conversation")
router.register(r"messages", MessageViewSet, basename="message")

urlpatterns = [
    # path("", include(router.urls)),
    path(
        "conversations/<int:pk>/add_message/",
        AddMessageAPIView.as_view(),
        name="add_message",
    ),
    path(
        "conversations/<int:pk>/soft_delete/",
        SoftDeleteConversationAPIView.as_view(),
        name="soft_delete_conversation",
    ),
]
