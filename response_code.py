from typing import Any

response_ru = {
    1: 'Успешное выполнение запроса.',
    2: 'Ошибка на стороне сервера.',
    3: 'Отказ в доступе со стороны сервера.'
}

response_en = {
    1: 'Successful completion of the request.',
    2: 'Server side error.',
    3: 'Server access denied.'
}


class ResponseCode():
    def __init__(self, code, data=None):
        self.answercode: int = code
        self.answer: str = response_en[code]
        self.data: Any = data

    def give_answer(self, request):
        if request.session.get('language') is None or request.session['language'] == 'en':
            return {
                    'answercode': self.answercode,
                    'answer': response_en[self.answercode],
                    'data': self.data
                    }
        else:
            return {
                    'answercode': self.answercode,
                    'answer': response_ru[self.answercode],
                    'data': self.data
                    }
