from celery import shared_task

from .models import AIResponse, Conversation, Message
from .utils import AImodel


@shared_task(bind=True)
def response_ai(self, message_id: int):
    current_message = Message.objects.get(id=message_id)
    current_conversation = current_message.conversation
    new_ai_response = AIResponse.objects.create(message=current_message)
    ai_model = AImodel(current_conversation)
    input_token = new_ai_response.get_input_token()
    status_code, response_text = ai_model.similator_ai_response(input_token)
    if status_code == AImodel.STATUS_SUCCESS:
        new_ai_response.mark_completed(response_text)
    elif status_code == AImodel.STATUS_FAIL:
        new_ai_response.mark_failed(response_text)
        if new_ai_response.retry_count < 3:
            raise self.retry(
                args=[message_id], countdown=5 * new_ai_response.retry_count
            )
