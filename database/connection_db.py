from .parameter_schemes import Config

import asyncpg
from asyncpg.pool import Pool

from settings import config
# from log.descriptionlogger import log_error, log_info



# формирование параметров для базы данных через базовую модель для избежания ошибок
config = Config(**config)


class JobDb():
    '''Класс реализации работы базы данных'''
    __pool = dict()

    def __init__(self):
        self.user: str = config.DataBase.user
        self.password: str = config.DataBase.password
        self.db_name: str = config.DataBase.db_name
        self.host: str = config.DataBase.host
        self.port: int = config.DataBase.port
        self.pool = None
        self.cursor = None

    async def __aenter__(self) -> Pool:
        '''аналог метода __enter__ под асинхрон
        В случае вызова класса и наличия активного пула возвращается пул подключения базы данных
        '''
        if self.pool:
            return self.pool
        self.cursor = await asyncpg.connect(user=self.user,
                                            password=self.password,
                                            database=self.db_name,
                                            host=self.host,
                                            port=self.port)
        return self.cursor

    async def __aexit__(self, exc_type, exc, tb):
        '''аналог метода __enter__ под асинхрон
        закрытие актовного курсора при работе непостедственно с запросом'''
        if self.cursor:
            await self.cursor.close()

    async def create_pool(self):
        '''Функция создания пула при запуске приложения
        так же сохранение активного пула в словаре для работы с ним'''
        try:
            name = 'root'
            self.pool: Pool = await asyncpg.create_pool(user=self.user,
                                                        password=self.password,
                                                        database=self.db_name,
                                                        host=self.host,
                                                        port=self.port)
            JobDb.__pool[name] = self.pool
            print(self.pool)
        except Exception as e:
            pass
            # log_error.error(f'При подключении к базе данных произошло исключение: {e}')

    async def close_pool(self):
        '''Функция завершения работы базы данных (отключение)
        закрывает все активные пулы к базе данных'''
        try:
            for name in JobDb.__pool.keys():
                await JobDb.__pool[name].close()
        except Exception as e:
            pass
            # log_error.error(f'При отключении базы данных произошло исключение: {e}')
