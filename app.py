import uvicorn

from fastapi import FastAPI, Request

from settings import HOST, PORT
from service.views import servis_router
from database.connection_db import JobDb
# from log.descriptionlogger import log_error, log_info
from starlette.middleware.sessions import SessionMiddleware


from fastapi.middleware.cors import CORSMiddleware

from service.auxiliary_views import background_folder_deletion as bfd



app = FastAPI(
    title='Сервис регистрации',
    version='0.0.1'
)


origins = [

    "http://localhost:1420",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:8082",
    "http://127.0.0.1:8083",
    "http://smtp.yandex.com:465"

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key="SECRET_KEY")



@app.on_event("startup")
async def on_startup():
    '''Функция подключени базы данных на старте приложения'''
    await JobDb().create_pool()
    await bfd()
    # log_info.info('База данных подклюбчена')


@app.on_event('shutdown')
async def shutdown_event():
    '''Функция отключения базы данных по окончанию работы'''
    await JobDb().close_pool()
    # log_info.info('База данных отключена')

app.include_router(servis_router)

if __name__ == '__main__':
    uvicorn.run(app,
                host=HOST,
                port=PORT)

