import pytest

from conversation.models import AIResponse, Conversation, Message
from genaibackend.users.models import User


@pytest.fixture
def user(db):
    return User.objects.create_user(email="testuser", password="password")


@pytest.fixture
def conversation(user):
    return Conversation.objects.create(user=user, title="Test Conversation")


@pytest.fixture
def message(conversation):
    return Message.objects.create(
        conversation=conversation, sender=Message.SENDER_USER, content="Hello"
    )


def test_conversation_creation(conversation, user):
    assert conversation.user == user
    assert conversation.title == "Test Conversation"
    assert conversation.status == Conversation.STATUS_ACTIVATE


def test_conversation_soft_delete(conversation):
    conversation.soft_delete()
    assert conversation.status == Conversation.STATUS_DELETE
    assert Conversation.all_objects.filter(id=conversation.id).exists()


def test_message_creation(message, conversation):
    assert message.conversation == conversation
    assert message.sender == Message.SENDER_USER
    assert message.content == "Hello"
    assert message.order == 1


def test_message_auto_increment_order(conversation):
    message1 = Message.objects.create(
        conversation=conversation, sender=Message.SENDER_USER, content="First"
    )
    message2 = Message.objects.create(
        conversation=conversation, sender=Message.SENDER_USER, content="Second"
    )
    assert message1.order == 1
    assert message2.order == 2


@pytest.fixture
def ai_response(message):
    return AIResponse.objects.create(
        message=message, response_content="AI Reply", status=AIResponse.STATUS_COMPLETED
    )


def test_ai_response_creation(ai_response, message):
    assert ai_response.message == message
    assert ai_response.response_content == "AI Reply"
    assert ai_response.status == AIResponse.STATUS_COMPLETED


def test_ai_response_mark_completed(ai_response):
    ai_response.mark_completed("New AI Response")
    assert ai_response.response_content == "New AI Response"
    assert ai_response.status == AIResponse.STATUS_COMPLETED


def test_ai_response_mark_failed(ai_response):
    ai_response.mark_failed("Error occurred")
    assert ai_response.retry_count == 1
    assert (
        ai_response.status == AIResponse.STATUS_GENERATING
        or ai_response.status == AIResponse.STATUS_ERROR
    )
