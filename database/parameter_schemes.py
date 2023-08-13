from pydantic import BaseModel

from fastapi import Query


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
    mail: str = Query(description='Почта пользователя')
    password: str = Query(description='Пароль для входа в приложение')


class Registration(BaseModel):
    mail: str = Query(description='Почта пользователя')
    password: str = Query(description='Пароль для входа')
    password_repeat: str = Query(description='Подтверждение введенного пароля')
    first_name: str = Query(description='Имя пользователя')
    last_name: str = Query(description='Фамилия пользователя')


class CodeReg(BaseModel):
    code: str = Query(description='Код подтверждения регистрации')
    public_key: str = Query(description='Открытый ключ')
    private_key: str = Query(description='Закрытый ключ')


class CodeAut(BaseModel):
    code: str = Query(description='Код подтверждения регистрации')