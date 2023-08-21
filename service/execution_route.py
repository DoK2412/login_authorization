import re
import random
import uuid
import hashlib
import os

from email_validate import validate, validate_or_fail
from database.connection_db import JobDb
from database.sql_requests import (NEW_USER, NEW_CODE, EMAIL_CHECK, CHECK_CODE, UPDATE_STATUS_PROFILE,
                                   UPDATE_STATUS_CONFIRM, CHECK_PASSWORD, INSERT_PUBLIC_PRIVATE_KEY,
                                   GET_PUBLIC_KEY, CHECK_UID, CREATE_FOLDER)
from datetime import datetime, timedelta

from service.user import User
from main import sendEmail
from settings import salt

import rsa
from cryptoprotection.cryptopro import load_public_key, load_private_key

from response_code import ResponseCode


user = User()


def generate_uuid5(salt_one, salt_two):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, str(salt_one) + str(salt_two) + str(uuid.uuid4()))).replace("-", "")


async def registration_user(mail: str,
                            password: str,
                            password_repeat: str,
                            first_name: str,
                            last_name: str):
    """
    Регистранция пользователя
    :param mail: эмейл
    :param password:  пароль
    :param password_repeat: подтверждения пароля
    :param first_name: Имя
    :param last_name: Фамилия
    :return:
    """

    if validate(
            email_address=mail,
            check_format=False,
            check_blacklist=False,
            check_dns=False,
            dns_timeout=10,
            check_smtp=False,
            smtp_debug=False) is False:
        return ResponseCode(10, 'Введенная почта не явзяется почтовым адресом')

    if re.match(r'^(?=.*[0-9].*)(?=.*[a-z].*)(?=.*[A-Z].*)(?=.*[,."\':;!@#$%^&*)(№?*-_].*)[0-9a-zA-Z]{8,}$', password) is None:
        return 'Пароль должен содержать 8 символов, буквы в верхнем и нижнем регистре и цифры'
    elif password != password_repeat:
        return ResponseCode(10, 'Введенные пароли не совпадают')

    if re.match(r'^[a-z]+$', first_name.lower()) or re.match(r'^[а-я]+$', first_name.lower()) is None:
        return ResponseCode(10, 'Имя не соответствует стандарту, использовано смешивание алфавитов')

    if re.match(r'^[a-z]+$', last_name.lower()) or re.match(r'^[а-я]+$', last_name.lower()) is None:
        return ResponseCode(10, 'Фамилия не соответствует стандарту, использовано смешивание алфавитов')


    code_rand = str(random.randrange(100000, 1000000))

    password = hashlib.pbkdf2_hmac('sha256',
                                   password.encode('utf-8'),
                                   salt,
                                   100000)
    async with JobDb() as connector:
        email_check = await connector.fetchval(EMAIL_CHECK, mail)
        if email_check:
            return ResponseCode(10,'Пользователь под данным эмейлом уже есть в базе данных')

        user.id = await connector.fetchval(NEW_USER, first_name, last_name, mail, password)
        date = datetime.now()
        exp_date = date + timedelta(seconds=600)
        await connector.fetchval(NEW_CODE, user.id, code_rand, date, exp_date)
    # отправка письма на почту
    await sendEmail(code_rand, mail)
    return ResponseCode(1, user.id)


async def confirm_user(requests, code: str, public_key: str, private_key: str ):
    '''
    Подтверждение регистрации пользоваткля
    :param code:
    :return:
    '''
    if code.isdigit() and len(code) == 6:
        async with JobDb() as connector:
            db_code = await connector.fetchrow(CHECK_CODE, user.id, code)
            if db_code and db_code['exp_date'] > datetime.now():
                uuid = generate_uuid5(user.id, datetime.now())
                await connector.fetchrow(UPDATE_STATUS_PROFILE, uuid, user.id)
                await connector.fetchrow(UPDATE_STATUS_CONFIRM, user.id, db_code['code'])
                await connector.fetchval(INSERT_PUBLIC_PRIVATE_KEY, user.id, public_key, private_key)
                await connector.fetchrow(CREATE_FOLDER, user.id, 'my_folder')
                return ResponseCode(1)
            elif db_code and db_code['exp_date'] < datetime.now():
                await connector.fetchrow(UPDATE_STATUS_CONFIRM, user.id, db_code['code'])
                return ResponseCode(9)
    else:
        return ResponseCode(10,'Код не верный')


async def authorization_user(requests,
                                email: str,
                                password: str):
    code_rand = str(random.randrange(100000, 1000000))
    async with JobDb() as connector:
        db_password = await connector.fetchrow(CHECK_PASSWORD, email)
        user.id = db_password['id']
        if db_password['active']:

            password = hashlib.pbkdf2_hmac('sha256',
                                           password.encode('utf-8'),
                                           salt,
                                           100000)

            if password == db_password['password']:
                date = datetime.now()
                exp_date = date + timedelta(seconds=600)
                await connector.fetchval(NEW_CODE, user.id, code_rand, date, exp_date)
                await sendEmail(code_rand, email)
                return ResponseCode(1)
            else:
                return ResponseCode(2,'Пароли не совпадают, повторите попытку')
        else:
            return ResponseCode(2,'Пользователь не найден либо аккаунт не подтвержден')


async def code_repetition(requests):
    async with JobDb() as connector:
            code_rand = str(random.randrange(100000, 1000000))
            date = datetime.now()
            exp_date = date + timedelta(seconds=600)
            await connector.fetchval(NEW_CODE, user.id, code_rand, date, exp_date)
            await sendEmail(code_rand)
            return ResponseCode(1,'Новый код отправлен на вашу почту')



async def confirm_user_aut(requests, code):
    '''
       Подтверждение авторизации пользоваткля
       :param code:
       :return:
       '''
    if code.isdigit() and len(code) == 6:
        async with JobDb() as connector:
            db_code = await connector.fetchrow(CHECK_CODE, user.id, code)
            if db_code and db_code['exp_date'] > datetime.now():
                await connector.fetchrow(UPDATE_STATUS_CONFIRM, user.id, db_code['code'])
                uid = await connector.fetchrow(CHECK_UID, user.id)
                return ResponseCode(1, uid['uid'])
            elif db_code and db_code['exp_date'] < datetime.now():
                await connector.fetchrow(UPDATE_STATUS_CONFIRM, user.id, db_code['code'])
                return ResponseCode(9)
    else:
        return ResponseCode(10, 'Код не верный')
