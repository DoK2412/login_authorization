from pydantic import BaseModel

from fastapi import Query

from typing import Optional


class DataBase(BaseModel):
    """
    Конфигурация Базы Данных
    """
    user: str
    password: str
    db_name: str
    host: str
    port: int


class Config(BaseModel):
    DataBase: DataBase


class Authorization(BaseModel):
    email: str = Query(description='Почта пользователя')
    password: str = Query(description='Пароль для входа в приложение')
    dev: bool = Query(default=False, description='Профиль разработчика')



class Registration(BaseModel):
    mail: str = Query(description='Почта пользователя')
    password: str = Query(description='Пароль для входа')
    password_repeat: str = Query(description='Подтверждение введенного пароля')
    first_name: str = Query(description='Имя пользователя')
    last_name: str = Query(description='Фамилия пользователя')
    dev: bool = Query(default=False, description='Профиль разработчика')



class CodeReg(BaseModel):
    code: str = Query(description='Код подтверждения регистрации')
    public_key: str = Query(description='Открытый ключ')
    private_key: str = Query(description='Закрытый ключ')


class CodeAut(BaseModel):
    code: str = Query(description='Код подтверждения регистрации')


class CodeConfirmation(BaseModel):
    email: str = Query(description='Почта пользователя')
    dev: bool = Query(default=False, description='Профиль разработчика')


class Profile(BaseModel):
    id: int
    uid: Optional[str]
    first_name: str
    last_name: str
    email: str
    active: bool