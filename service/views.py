from fastapi import APIRouter, Request

from database.parameter_schemes import Authorization, Registration, CodeReg, CodeAut, CodeConfirmation
from .execution_route import registration_user, confirm_user, authorization_user, code_repetition, confirm_user_aut, profile

from log.descriptionlogger import log_error
from response_code import ResponseCode

servis_router = APIRouter(
    prefix='/registration'
)


@servis_router.post('/registration')
async def registration(requests: Request,
                       user: Registration):
    try:
        result = await registration_user(requests,
                                         user.mail,
                                         user.password,
                                         user.password_repeat,
                                         user.first_name,
                                         user.last_name,
                                         user.dev)
        return result
    except Exception as exc:
        log_error.error(f'При выполнении произошла ошибка {exc}')
        return ResponseCode(2, 'internalError').give_answer(requests)


@servis_router.post('/confirmRegistration')
async def confirm(requests: Request,
                  code: CodeReg):
    try:
        result = await confirm_user(requests,
                                    code.code,
                                    code.public_key,
                                    code.private_key
                                    )
        return result
    except Exception as exc:
        log_error.error(f'При выполнении произошла ошибка {exc}')
        return ResponseCode(2, 'internalError').give_answer(requests)
@servis_router.post('/authorization')
async def authorization(requests: Request,
                        user: Authorization):
    try:
        result = await authorization_user(requests,
                                    user.email,
                                    user.password,
                                    user.dev)
        return result
    except Exception as exc:
        log_error.error(f'При выполнении произошла ошибка {exc}')
        return ResponseCode(2, 'internalError').give_answer(requests)

@servis_router.post('/codeRepetition')
async def codeRepetition(requests: Request,
                         email: CodeConfirmation):
    try:
        result = await code_repetition(requests, email.email, email.dev)
        return result
    except Exception as exc:
        log_error.error(f'При выполнении произошла ошибка {exc}')
        return ResponseCode(2, 'internalError').give_answer(requests)

@servis_router.post('/confirmAuthorizationh')
async def confirm(requests: Request,
                  code: CodeAut):
    try:
        result = await confirm_user_aut(requests,
                                    code.code,
                                    )
        return result
    except Exception as exc:
        log_error.error(f'При выполнении произошла ошибка {exc}')
        return ResponseCode(2, 'internalError').give_answer(requests)
@servis_router.get('/profile')
async def get_profile(requests: Request):
    try:
        result = await profile(requests)
        return ResponseCode(1, result)
    except Exception as exc:
        log_error.error(f'При выполнении произошла ошибка {exc}')
        return ResponseCode(2, 'internalError').give_answer(requests)