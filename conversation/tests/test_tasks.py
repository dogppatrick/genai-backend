from unittest.mock import MagicMock, patch

import pytest
from celery.result import EagerResult

from conversation.models import AIResponse, Conversation, Message
from conversation.tasks import auto_title, response_ai
from conversation.utils import FakeAImodel
from genaibackend.users.models import User


@pytest.fixture
def user(db):
    return User.objects.create_user(email="testuser", password="testpassword")


@pytest.mark.django_db
@patch("conversation.tasks.FakeAImodel.similator_ai_response")
@patch("conversation.tasks.AIResponse.objects.get")
@patch("conversation.tasks.AIResponse.objects.filter")
@patch("conversation.tasks.Message.objects.get")
def test_response_ai(
    mock_message_get,
    mock_ai_response_filter,
    mock_ai_response_get,
    mock_fake_ai_model_similator_ai_response,
    user,
):
    fake_conversation = Conversation.objects.create(user=user)
    fake_message = Message.objects.create(
        content="Test message", conversation=fake_conversation
    )
    fake_ai_response = AIResponse.objects.create(message=fake_message)
    mock_message_get.return_value = fake_message
    mock_ai_response_filter.return_value = [fake_ai_response]
    mock_ai_response_get.return_value = fake_ai_response
    mock_fake_ai_model_similator_ai_response.return_value = (
        FakeAImodel.STATUS_SUCCESS,
        "fake_response_result",
    )
    response_ai(fake_message.id)

    assert fake_ai_response.status == AIResponse.STATUS_COMPLETED


@pytest.mark.django_db
@patch("conversation.tasks.FakeAImodel")
@patch("conversation.tasks.AIResponse.objects.create")
@patch("conversation.tasks.get_task_logger")
def test_response_ai_retry(
    mock_logger, mock_ai_response_create, mock_fake_ai_model, user
):
    fake_conversation = Conversation.objects.create(user=user)
    fake_message = Message.objects.create(
        content="Test message", conversation=fake_conversation
    )
    fake_ai_response = MagicMock(spec=AIResponse)
    fake_ai_response.message = fake_message
    fake_ai_response.status = AIResponse.STATUS_GENERATING
    mock_ai_response_create.return_value = fake_ai_response
    fake_ai_model = MagicMock(spec=FakeAImodel)
    fake_ai_model.similator_ai_response.return_value = (
        FakeAImodel.STATUS_FAIL,
        "Error generating response",
    )
    mock_fake_ai_model.return_value = fake_ai_model
    fake_ai_response.retry_count = 2
    with pytest.raises(Exception):
        response_ai(fake_message.id)

    fake_ai_response.retry_count += 1


@pytest.mark.django_db
@patch("conversation.tasks.FakeAImodel.create_title")
@patch("conversation.tasks.Message.objects.get")
def test_auto_title(get_message, mock_fake_ai_model_create_title, user):
    fake_conversation = Conversation.objects.create(title="Old Title", user=user)
    fake_message = Message.objects.create(
        content="Sample message for AI to generate title",
        conversation=fake_conversation,
    )
    mock_fake_ai_model_create_title.return_value = "test_title"
    get_message.return_value = fake_message
    auto_title(fake_conversation.id)
    fake_conversation.refresh_from_db()
    assert fake_conversation.title == "test_title"
