from fastapi import APIRouter, Request

from database.parameter_schemes import Authorization, Registration, CodeReg, CodeAut
from .execution_route import registration_user, confirm_user, authorization_user, code_repetition, confirm_user_aut

servis_router = APIRouter(
    prefix='/registration'
)


@servis_router.post('/registration')
async def registration(requests: Request,
                       user: Registration):
    result = await registration_user(user.mail,
                                     user.password,
                                     user.password_repeat,
                                     user.first_name,
                                     user.last_name)
    return result


@servis_router.post('/confirmRegistration')
async def confirm(requests: Request,
                  code: CodeReg):
    result = await confirm_user(requests,
                                code.code,
                                code.public_key,
                                code.private_key
                                )
    return result


@servis_router.post('/authorization')
async def authorization(requests: Request,
                        user: Authorization):
    result = await authorization_user(requests,
                                user.mail,
                                user.password)
    return result


@servis_router.get('/codeRepetition')
async def codeRepetition(requests: Request):
    result = await code_repetition(requests)
    return result


@servis_router.post('/confirmAuthorizationh')
async def confirm(requests: Request,
                  code: CodeAut):
    result = await confirm_user_aut(requests,
                                code.code,
                                )
    return result