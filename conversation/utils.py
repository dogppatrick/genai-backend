import secrets


class AImodel:
    STATUS_SUCCESS = "success"
    STATUS_FAIL = "fail"

    def __init__(self, model_name: str = "gpt-4"):
        self.model_name = model_name

    def create_resposne(self, input_token: str):
        response_message = "假設 ai 回應了以下訊息"
        return self.STATUS_SUCCESS, response_message

    def ai_response_error(self, input_token: str):
        error_message = "錯誤"
        return self.STATUS_FAIL, error_message

    def similator_ai_response(self, input_token: str):
        f = secrets.choice([self.create_resposne, self.ai_response_error])
        return f(input_token)
