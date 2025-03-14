import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from conversation.models import Conversation, Message
from genaibackend.users.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(email="testuser", password="password")


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def conversation(user):
    return Conversation.objects.create(user=user, title="Test Conversation")


@pytest.fixture
def message(conversation):
    return Message.objects.create(
        conversation=conversation, sender=Message.SENDER_USER, content="Hello"
    )


def test_list_conversations(auth_client, conversation):
    url = reverse("conversation-list")
    response = auth_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1


def test_create_conversation(auth_client):
    url = reverse("conversation-list")
    data = {"title": "New Conversation"}
    response = auth_client.post(url, data)
    assert response.status_code == status.HTTP_201_CREATED
    assert Conversation.objects.count() == 1


def test_update_conversation(auth_client, conversation):
    url = reverse("conversation-detail", args=[conversation.id])
    data = {"title": "Updated Title"}
    response = auth_client.patch(url, data)
    assert response.status_code == status.HTTP_200_OK
    conversation.refresh_from_db()
    assert conversation.title == "Updated Title"


def test_delete_conversation(auth_client, conversation):
    url = reverse("conversation-detail", args=[conversation.id])
    response = auth_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Conversation.objects.count() == 0


def test_edit_message(auth_client, message):
    url = reverse("message-edit-message", args=[message.id])
    data = {"content": "Updated Message"}
    response = auth_client.patch(url, data)
    assert response.status_code == status.HTTP_200_OK
    message.refresh_from_db()
    assert message.content == "Updated Message"
    assert message.is_edited is True


def test_mark_message_deleted(auth_client, message):
    url = reverse("message-mark-deleted", args=[message.id])
    response = auth_client.patch(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    message.refresh_from_db()
    assert message.is_deleted is True
