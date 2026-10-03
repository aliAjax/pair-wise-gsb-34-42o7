from src.constants.error_codes import ERROR_CODES
from src.constants.error_messages import ERROR_MESSAGES

class BusinessError(Exception):
    """复核链业务异常：service 抛出，controller 包装成 HTTP 响应。"""
    def __init__(self, code, status=400, message=None):
        self.code = ERROR_CODES.get(code, code)
        self.status = status
        self.message = message or ERROR_MESSAGES.get(self.code, self.code)
        super().__init__(self.message)
