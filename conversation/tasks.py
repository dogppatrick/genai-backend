from celery import shared_task
from celery.utils.log import get_task_logger

from .models import AIResponse, Conversation, Message
from .utils import FakeAImodel

celery_logger = get_task_logger(__name__)


@shared_task(bind=True)
def response_ai(self, message_id: int):
    message = Message.objects.get(id=message_id)
    if not AIResponse.objects.filter(message=message):
        ai_response = AIResponse.objects.create(
            message=message, status=AIResponse.STATUS_GENERATING
        )
    ai_response = AIResponse.objects.get(message=message)
    celery_logger.info(f"ai response : {ai_response.id} start to generator")
    current_conversation = message.conversation
    ai_model = FakeAImodel(current_conversation.model_version)
    input_token = ai_response.get_input_token()
    status_code, response_text = ai_model.similator_ai_response(input_token)
    if status_code == FakeAImodel.STATUS_SUCCESS:
        ai_response.mark_completed(response_text)
        celery_logger.info(f"message : {ai_response.message} competed")
    elif status_code == FakeAImodel.STATUS_FAIL:
        ai_response.mark_failed(response_text)
        celery_logger.info(f"message : {ai_response.message} fail")
        if ai_response.retry_count < 3:
            raise self.retry(args=[message_id], countdown=5 * ai_response.retry_count)
        else:
            celery_logger.info(f"message : {ai_response.message} fail over retry count")


@shared_task()
def auto_title(conversation_id: int):
    ai_model = FakeAImodel()
    con = Conversation.objects.get(id=conversation_id)
    input_token = Message.objects.filter(conversation=con).first().content
    new_title = ai_model.create_title(input_token)
    con.title = new_title
    con.save()
