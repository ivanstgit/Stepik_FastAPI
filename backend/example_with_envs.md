# Конфигурируем наше приложение FastAPI
Давайте немного заполним структуру проекта.

Начнем с файла todo.py в эндпоинтах (накидаем рыбу):

from fastapi import APIRouter


todo_router = APIRouter(
    prefix="/todo",
    tags=["ToDo"]
)


@todo_router.get("/")
async def get_todos():
    pass


@todo_router.post("/")
async def create_todo():
    pass
Что мы сделали? Мы создали роутер (рассказывалось в уроке 8.1), чтобы потом его подключить к основному приложению. Так нам проще будет контролировать, какие группы конечных точек у нас открыты.

Давайте тогда его подключим к приложению в файле main.py:

import uvicorn
from fastapi import FastAPI

from app.api.endpoints.todo import todo_router


app = FastAPI()

app.include_router(todo_router)

if __name__ == "__main__":
    uvicorn.run(app="main:app")
Нам останется три настройки. 1-я - .env файл (заполняйте его своими данными):

DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASS=postgres
DB_NAME=my_db
2-я настройка - это файл config.py:

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def ASYNC_DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"


settings = Settings()
В конфиге можно держать и прокидывать между файлами все переменные окружения, которые нам нужны (например, соль к паролю, время жизни JWT-токена, алгоритм шифрования, api-ключи и всё такое прочее). В нашем примере он содержит только информацию для взаимодействия с БД, при чем вполне конкретной - учимся работать с постгресом. Как видите, работать с БД мы будем асинхронно (свойство класса - асинхронный урл нашей БД, который собирается из переменных окружения). Для корректной работы нам потребуется установить библиотеку pydantic-settings:

pip install pydantic-settings
Вместо этой библиотеки можете использовать любую другую, работающую с виртуальным окружением (напр. python-dotenv, environs), на ваш вкус (само собой изменив код конфига).

И 3-я настройка - это файл database.py. Если для синхронной версии он мог бы выглядеть как-то так:

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


DATABASE_URL = settings.DATABASE_URL  # у нас в settings'ах нет такого урла, но можно было бы добавить, поменяв драйвер на psycopg2

engine = create_engine(DATABASE_URL)

sync_session_maker = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = sync_session_maker()
    try:
        yield db
    finally:
        db.close()
То для асинхронной работы с БД наш файл database.py будет выглядеть так:

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


engine = create_async_engine(settings.ASYNC_DATABASE_URL)  # создали движок БД
async_session_maker = async_sessionmaker(engine, class_=AsyncSession)  # передали наш движок в создатель сессий


class Base(DeclarativeBase):
    pass
Класс Base - это условно метатаблица, которая нам потом позволит создавать модели SQLAlchemy, отслеживать все изменения и пр. Также в ней можно создать для всех моделей таблицы общий метод (например __str__ или __repr__, которые нормально показывали бы наши таблицы в админке/при print'е объектов).

Теперь можете запустить приложение (из мэйна или в командной строке) и проверить всё ли работает.