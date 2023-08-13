import uvicorn

from fastapi import FastAPI, Request

from settings import HOST, PORT
from service.views import servis_router
from database.connection_db import JobDb
from log.descriptionlogger import log_error, log_info


app = FastAPI(
    title='Сервис регистрации',
    version='0.0.1'
)


@app.on_event("startup")
async def on_startup():
    '''Функция подключени базы данных на старте приложения'''
    await JobDb().create_pool()
    log_info.info('База данных подклюбчена')


@app.on_event('shutdown')
async def shutdown_event():
    '''Функция отключения базы данных по окончанию работы'''
    await JobDb().close_pool()
    log_info.info('База данных отключена')

app.include_router(servis_router)

if __name__ == '__main__':
    uvicorn.run(app,
                host=HOST,
                port=PORT)

