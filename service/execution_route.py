import re
import random
import uuid
import hashlib
import os

from email_validate import validate, validate_or_fail
from database.connection_db import JobDb
from database.sql_requests import (NEW_USER, NEW_CODE, EMAIL_CHECK, CHECK_CODE, UPDATE_STATUS_PROFILE,
                                   UPDATE_STATUS_CONFIRM, CHECK_PASSWORD, INSERT_PUBLIC_PRIVATE_KEY,
                                   GET_PROFILE, CHECK_UID, CREATE_FOLDER)
from database.parameter_schemes import Profile
from datetime import datetime, timedelta

from service.user import User

from main import sendEmail
from settings import salt

from log.descriptionlogger import log_error, log_info


import rsa
from cryptoprotection.cryptopro import load_public_key, load_private_key

from response_code import ResponseCode


user = User()


def generate_uuid5(salt_one, salt_two):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, str(salt_one) + str(salt_two) + str(uuid.uuid4()))).replace("-", "")


async def registration_user(requests,
                            mail: str,
                            password: str,
                            password_repeat: str,
                            first_name: str,
                            last_name: str,
                            dev: bool):
    """
    Регистранция пользователя
    :param mail: эмейл
    :param password:  пароль
    :param password_repeat: подтверждения пароля
    :param first_name: Имя
    :param last_name: Фамилия
    :return:
    """
    try:
        if validate(
                email_address=mail,
                check_format=False,
                check_blacklist=False,
                check_dns=False,
                dns_timeout=10,
                check_smtp=False,
                smtp_debug=False) is False:
            log_info.info(f'Введенный эмейл при регистрации не соответствует стандарту {mail}')
            return ResponseCode(2, 'mailError').give_answer(requests)

        if re.match(r'^(?=.*[0-9].*)(?=.*[a-z].*)(?=.*[A-Z].*)(?=.*[,."\':;!@#$%^&*)(№?*-_].*)[0-9a-zA-Z]{8,}$', password) is None:
            log_info.info(f'Введенный пароль при регистрации не соответствует стандарту {password}')
            return ResponseCode(2, 'passwordErrorValid').give_answer(requests)
        elif password != password_repeat:
            log_info.info(f'Введенные пароли при регистрации не совпалают {mail}')
            return ResponseCode(2, 'passwordError').give_answer(requests)

        if re.match(r'^[a-z]+$', first_name.lower()) or re.match(r'^[а-я]+$', first_name.lower()):
            pass
        else:
            first_name = None

        if first_name is None:
            log_info.info(f'Попытка зарегистрироваться с именем смешанных алфавитов {first_name}')
            return ResponseCode(2, 'nameError').give_answer(requests)

        if re.match(r'^[a-z]+$', last_name.lower()) or re.match(r'^[а-я]+$', last_name.lower()):
            pass
        else:
            last_name = None

        if last_name is None:
            log_info.info(f'Попытка зарегистрироваться с фамилией смешанных алфавитов {last_name}')
            return ResponseCode(2, 'surnameError').give_answer(requests)

        if dev:
            code_rand = '666666'
        else:
            code_rand = str(random.randrange(100000, 1000000))

        password = hashlib.pbkdf2_hmac('sha256',
                                       password.encode('utf-8'),
                                       salt,
                                       100000)
        async with JobDb() as connector:
            email_check = await connector.fetchrow(EMAIL_CHECK, mail)
            if email_check:
                if email_check['active'] == False:
                    return ResponseCode(15, email_check['id'])
                log_info.info(f'Попытка зарегистрироваться под существующим эмейлом {mail}')
                return ResponseCode(2, 'userError').give_answer(requests)

            date = datetime.now()
            user.id = await connector.fetchval(NEW_USER, first_name, last_name, mail, date, password)
            exp_date = date + timedelta(seconds=600)
            await connector.fetchval(NEW_CODE, user.id, code_rand, date, exp_date, 'registration')
        # отправка письма на почту
        await sendEmail(code_rand, mail)
        log_info.info(f'Пользователь успешно зарегистрировался под эмейлом {mail}')

        return ResponseCode(1, user.id)
    except Exception as exc:
        log_error.error(f'При выполнении произошла ошибка {exc}')
        return ResponseCode(2, 'internalError').give_answer(requests)


async def confirm_user(requests, code: str, public_key: str, private_key: str ):
    '''
    Подтверждение регистрации пользоваткля
    :param code:
    :return:
    '''
    try:
        if code.isdigit() and len(code) == 6:
            async with JobDb() as connector:
                db_code = await connector.fetchrow(CHECK_CODE, int(requests.cookies['user_id']), code)
                if db_code is None:
                    log_info.info(f'Пользователь {user.id} ввел неверный код подтверждения {code} при регистрации')
                    return ResponseCode(2, 'codeError').give_answer(requests)
                if db_code and db_code['exp_date'] > datetime.now():
                    uuid = generate_uuid5(int(requests.cookies['user_id']), datetime.now())
                    await connector.fetchrow(UPDATE_STATUS_PROFILE, uuid, int(requests.cookies['user_id']))
                    await connector.fetchrow(UPDATE_STATUS_CONFIRM, int(requests.cookies['user_id']))
                    await connector.fetchval(INSERT_PUBLIC_PRIVATE_KEY, int(requests.cookies['user_id']), public_key, private_key)
                    await connector.fetchrow(CREATE_FOLDER, int(requests.cookies['user_id']), 'my_folder')
                    log_info.info(f'Пользователь {user.id} успешно закончил регистрацию')
                    return ResponseCode(1, 'registrationOk').give_answer(requests)
                elif db_code and db_code['exp_date'] < datetime.now():
                    await connector.fetchrow(UPDATE_STATUS_CONFIRM, int(requests.cookies['user_id']), db_code['code'])
                    log_info.info(f'Срок активности кода регистрации введенного пользователем {user.id} истек')
                    return ResponseCode(2, 'codeError').give_answer(requests)
        else:
            log_info.info(f'Пользователь {user.id} ввел код {code} не соответствующий стандарту при регистрации')
            return ResponseCode(2, 'codeError').give_answer(requests)
    except Exception as exc:
        log_error.error(f'При выполнении произошла ошибка {exc} при регистрации')
        return ResponseCode(2, 'internalError').give_answer(requests)


async def authorization_user(requests,
                            email: str,
                            password: str,
                            dev):
    try:
        if dev:
            code_rand = '666666'
        else:
            code_rand = str(random.randrange(100000, 1000000))
        async with JobDb() as connector:
            db_password = await connector.fetchrow(CHECK_PASSWORD, email)
            if db_password is None:
                log_info.info(f'Пользователя под эмейлом {email} не найдено в базе данных при авторизации')
                return ResponseCode(2, 'logPassError').give_answer(requests)
            else:
                user.id = db_password['id']
            if db_password['active']:

                password = hashlib.pbkdf2_hmac('sha256',
                                               password.encode('utf-8'),
                                               salt,
                                               100000)

                if password == db_password['password']:
                    date = datetime.now()
                    exp_date = date + timedelta(seconds=600)
                    await connector.fetchval(NEW_CODE, user.id, code_rand, date, exp_date, 'authorization')
                    await sendEmail(code_rand, email)
                    return ResponseCode(1, 'authorizationOK').give_answer(requests)
                else:
                    log_info.info(f'Введенный пароль пользователем {email} не совпал, отказано в доступе')
                    return ResponseCode(2, 'logPassError').give_answer(requests)
            else:
                log_info.info(f'Аккаунт пользователя {email} не подтвержден')
                return ResponseCode(2, 'accountError').give_answer(requests)
    except Exception as exc:
        log_error.error(f'При выполнении произошла ошибка {exc}')
        return ResponseCode(2, 'internalError').give_answer(requests)


async def code_repetition(requests, email, dev):
    try:
        async with JobDb() as connector:
            if dev:
                code_rand = '666666'
            else:
                code_rand = str(random.randrange(100000, 1000000))
            date = datetime.now()
            exp_date = date + timedelta(seconds=600)
            await connector.fetchrow(UPDATE_STATUS_CONFIRM, int(requests.cookies['user_id']))
            await connector.fetchval(NEW_CODE, int(requests.cookies['user_id']), code_rand, date, exp_date, 'repeat')
            await sendEmail(code_rand, email)
            log_info.info(f'Отправлен повторный код подтверждения на эмейл {email}')
            return ResponseCode(1, 'newCode').give_answer(requests)
    except Exception as exc:
        log_error.error(f'При выполнении произошла ошибка {exc}')
        return ResponseCode(2, 'internalError').give_answer(requests)


async def confirm_user_aut(requests, code):
    '''
       Подтверждение авторизации пользователя
       :param code:
       :return:
       '''
    try:
        if code.isdigit() and len(code) == 6:
            async with JobDb() as connector:
                db_code = await connector.fetchrow(CHECK_CODE, user.id, code)
                if db_code is None:
                    log_info.info(f'Получен не активный код от пользователя {user.id}')
                    return ResponseCode(2, 'codeError').give_answer(requests)
                if db_code and db_code['exp_date'] > datetime.now():
                    await connector.fetchrow(UPDATE_STATUS_CONFIRM, user.id)
                    uid = await connector.fetchrow(CHECK_UID, user.id)
                    log_info.info(f'Успешная авторизация пользователя {user.id}')
                    return ResponseCode(1, uid['uid']).give_answer(requests)
                elif db_code and db_code['exp_date'] < datetime.now():
                    await connector.fetchrow(UPDATE_STATUS_CONFIRM, user.id)
                    log_info.info(f'Срок жизни кода подтверждения {code} истек для пользователя {user.id}')
                    return ResponseCode(2, 'codeError').give_answer(requests)
        else:
            log_info.info(f'Получен не верный код подтверждения {code} от пользователя {user.id}')
            return ResponseCode(2, 'codeError').give_answer(requests)
    except Exception as exc:
        log_error.error(f'При выполнении произошла ошибка {exc}')
        return ResponseCode(2, 'internalError').give_answer(requests)


async def profile(requests):
    ''''
        Получение профиля пользователя
    '''
    try:
        session_uid = requests.cookies['user_uid']
        async with JobDb() as connector:
            profile = await connector.fetchrow(GET_PROFILE, session_uid)
            if profile:
                profile_valid = Profile(**profile)
                log_info.info(f'Пользователь {profile_valid.email} запросил сведения о профиле')
                return profile_valid
            else:
                log_info.info(f'Пользователь не найдей в базе данных')
                return ResponseCode(2, 'userNot').give_answer(requests)
    except Exception as exc:
        log_error.error(f'При выполнении произошла ошибка {exc}')
        return ResponseCode(2, 'internalError').give_answer(requests)
