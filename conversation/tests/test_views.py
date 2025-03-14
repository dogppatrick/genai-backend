from unittest.mock import patch

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from conversation.models import Conversation, Message
from genaibackend.users.models import User
from genaibackend.users.utils import generate_jwt


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(email="testuser", password="testpassword")


@pytest.fixture
def auth_client(api_client, user):
    token = generate_jwt(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return api_client


@pytest.fixture
def not_auth_client(api_client, user):
    return api_client


@pytest.fixture
def conversation(user):
    return Conversation.objects.create(user=user)


@pytest.mark.django_db
@patch("conversation.views.response_ai.apply_async")
@patch("conversation.views.auto_title.apply_async")
def test_start_new_conversation(mock_auto_title, mock_response_ai, auth_client):
    url = reverse("start_conversation")
    data = {"content": "Hello, AI!", "model_version": "gpt-4"}
    response = auth_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert Conversation.objects.count() == 1
    assert Message.objects.count() == 2
    assert Message.objects.filter(
        sender=Message.SENDER_USER, content="Hello, AI!"
    ).exists()


@pytest.mark.django_db
@patch("conversation.views.response_ai.apply_async")
@patch("conversation.views.auto_title.apply_async")
def test_start_new_conversation_missing_content(
    mock_auto_title, mock_response_ai, auth_client
):
    url = reverse("start_conversation")
    response = auth_client.post(url, {}, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "error" in response.data


@pytest.mark.django_db
@patch("conversation.views.response_ai.apply_async")
def test_add_message(mock_response_ai, auth_client, conversation):
    url = reverse("add_message", kwargs={"pk": conversation.id})
    data = {"content": "How are you?"}

    response = auth_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert Message.objects.count() == 2
    assert Message.objects.filter(
        sender=Message.SENDER_USER, content="How are you?"
    ).exists()


@pytest.mark.django_db
@patch("conversation.views.response_ai.apply_async")
def test_add_message_missing_content(mock_response_ai, auth_client, conversation):
    url = reverse("add_message", kwargs={"pk": conversation.id})
    response = auth_client.post(url, {}, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "error" in response.data


@pytest.mark.django_db
@patch("conversation.views.response_ai.apply_async")
def test_add_message_nonexistent_conversation(mock_response_ai, auth_client):
    url = reverse("add_message", kwargs={"pk": 9999})
    data = {"content": "This conversation does not exist"}

    response = auth_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "error" in response.data
