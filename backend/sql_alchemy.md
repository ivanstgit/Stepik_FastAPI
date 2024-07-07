Полный код проекта находится по ссылке https://github.com/Cheater121/sqlalchemy_postgres_fastapi/tree/master. 
# Создание моделей SQLAlchemy
Есть два способа объявления моделей алхимии (декларативный и императивный), но мы не будем вам рассказывать про второй, так как с выходом SQLAlchemy 2.0 в нем необходимость отпала. Будем сразу рассказывать самый свежак.

С алхимией 2.0 у нас появилась возможность переводить (маппать) питонячьи типы данных на типы SQL.

Давайте для модельки ToDo возьмем условие из задания 5.1:

Создайте модель данных (схему) для простого ресурса (например, элемента "Todo" (воображаемый список дел), который включает такие поля, как "id", "title" (заголовок), "description" (описание) и "completed" (завершено). И расширим временем создания (чтобы было побольше примеров работы с полями таблицы перед глазами).

В коде в models.py это выглядело бы так (комментарии даны по коду):

```import datetime

from sqlalchemy import BigInteger, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class ToDo(Base):  # обязательно наследуем все модели от нашей Base-метатаблицы
    __tablename__ = "todo"  # Указываем как будет называться наша таблица в базе данных (пишется в ед. числе)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)  # Строка  говорит, что наша колонка будет интом, но уточняет, что ещё и большим интом (актуально для ТГ-ботов), первичным ключом и индексироваться
    description: Mapped[str]  # Описание, просто строка; если нужно дополнительные условия добавить, то mapped_column
    completed: Mapped[bool] = mapped_column(default=False)  # Задали значение по-умолчанию False
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())  # просто для примера

# Код выше аналогичен этим устаревшим примерам:

# todo = Table("todo", metadata,
#              Column("id", BigInteger, primary_key=True, index=True),
#              Column("description", String),
#              Column("completed", Boolean, default=False),
#              Column("created_at", DateTime, nullable=False, server_default=func.now())
#              )

# class ToDo(Base):
#     __tablename__ = "todo"
#
#     id = Column(BigInteger, primary_key=True, index=True)
#     description = Column(String)
#     completed = Column(Boolean, default=False)
#     created_at = Column(DateTime, nullable=False, server_default=func.now())
Соответственно, мы указали типы данных, перевели их на манер SQL при помощи Mapped, некоторые уточнили с помощью mapped_column.
```

# Установка и настройка Alembic
Если вы в уроке 5.3 не смогли настроить alembic, то самое время это сделать, потому что вся модернизация нашей базы данных будет происходить через него.

Теоретически, можно было бы через lifespan создавать модели БД, например так:
```
# этот код лежал бы в main.py с маленьким дополнением в части его передачи в экземпляр FastAPI, 
# и при создании приложения мы бы создавали все модели БД
# но это плохая практика и плохо с историей изменений

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
```
Но мы планируем в будущем менять нашу базу данных, поэтому нам нужен аналог гитхаба для нашей БД - alembic.

Выполняем команду (желательно находясь в виртуальном окружении проекта):

`pip install alembic`

Далее инициируем alembic баш-командой (находясь в папке проекта):

`alembic init alembic`

После этого можно приступать к настройке алембика:

1) Открываем alembic.ini и находим строчку: 

`sqlalchemy.url = driver://user:pass@localhost/dbname`
Меняем её следующим образом:

`sqlalchemy.url = postgresql+psycopg2://%(DB_USER)s:%(DB_PASS)s@%(DB_HOST)s:%(DB_PORT)s/%(DB_NAME)s`
Такой формат (%(...)s) позволяет нам вставить на это место некоторую переменную. Подробнее написано прямо на первой странице документации алембика, если добрались до чтения в уроке 5.3. Все остальные строчки файла оставляем без изменений.

П.С. можно сделать и с асинхронным движком (`alembic init -t async alembic`), но в таком случае не на всех ОС'ях всё работает гладко - иногда разрывает асинхронное соединение и надо колдовать (см. документацию + стэковерфлоу). Поэтому показывается пример, который будет работать железобетонно.

2) Далее в папке alembic в проекте (должна была создаться после инициализации алембика) находим файл env.py, и меняем его следующим образом:
```
import os  # Добавили импорт os для извлечения из окружения наших переменных
import sys  # Добавили импорт модуля sys для работы с путями 
# (sys нужен для дальнейших импортов, иначе алембик не увидит нашу app папку)

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool

# Тут добавили в пути нашу папку app, чтобы алембик её увидел. 
# Порядок импортов специально нарушен, т.к. код выполняется построчно
sys.path.append(os.path.join(sys.path[0], 'app'))

from app.core.config import settings  # Добавили импорт нашего конфига
from app.db.database import Base  # Добавили импорт нашей мета-БД
from app.db.models import ToDo  # Добавили импорт модели, чтобы она инициализировалась, но она не используется
# без этого импорта алембик может не увидеть наши модели и создаст пустую миграцию


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Добавили работу с секциями конфига / работу с переменными окружения, чтобы они стали доступны в alembic.ini
section = config.config_ini_section
config.set_section_option(section, "DB_HOST", settings.DB_HOST)
config.set_section_option(section, "DB_PORT", settings.DB_PORT)
config.set_section_option(section, "DB_USER", settings.DB_USER)
config.set_section_option(section, "DB_NAME", settings.DB_NAME)
config.set_section_option(section, "DB_PASS", settings.DB_PASS)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata  # И последнее - дописали, что наша целевая метаинформация содержится в классе Base

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

```
Мы поменяли только часть кода, но для удобства приведен полный код - к измененным частям дополнены комментарии по коду.

​​​​​​​Обратите внимание, что колдовать пришлось с импортами, зато у нас папка alembic находится на одном уровне с app, то есть мы не привязаны к ОС машины (например, если инициировать алембик командой для виндовс `alembic init app\alembic`, для линукс `alembic init app/alembic`, то на винде в alembic.ini строчка `script_location = alembic` выглядела бы соответственно `script_location = app\alembic`, а на Linux'е `script_location = app/alembic`, что затруднило бы работу с мультиплатформенными докер-контейнерами).

Теперь можно наконец запускать наши миграции:

3) Выполняем команду:

`alembic revision --autogenerate -m 'initial'`

Если параметры указали в .env файле корректные, то миграция должна создаться.

4) Применяем миграцию:

`alembic upgrade head`
Теперь в нашей базе данных есть таблица "todo". После этого все изменения в наших моделях нужно прогонять через миграции (хорошая практика: изменение одной модели = 1 миграция).

Теперь мы можем внедрять код по работе с базой данных.

# Работа с базой данных в эндпоинтах
Сейчас покажем варианты, как обычно работа с базой данных реализуется на начальном уровне.

Для начала определим pydantic-модели в папке schemas в файле todo.py:
```
import datetime

from pydantic import BaseModel


class ToDoCreate(BaseModel):
    description: str
    completed: bool | None = False


class ToDoFromDB(ToDoCreate):  # будем возвращать из БД - унаследовались от создания и расширили 2 полями
    id: int
    created_at: datetime.datetime
Тогда наши маршруты могли бы стать такими:

from fastapi import APIRouter
from sqlalchemy import select

from app.api.schemas.todo import ToDoFromDB, ToDoCreate
from app.db.database import async_session_maker
from app.db.models import ToDo

todo_router = APIRouter(
    prefix="/todo",
    tags=["ToDo"]
)


@todo_router.get("/", response_model=list[ToDoFromDB])  # маршрут получения списка ToDo
async def get_todos():
    async with async_session_maker() as session:
        result = await session.execute(select(ToDo))
        return result.scalars().all()


@todo_router.post("/", response_model=ToDoFromDB)  # маршрут создания ToDo, принимает 2 поля, возвращает 4
async def create_todo(todo: ToDoCreate):
    async with async_session_maker() as session:
        new_todo = ToDo(**todo.model_dump())
        session.add(new_todo)
        await session.commit()
        await session.refresh(new_todo)
        return new_todo
```
Проблема при таком подходе в том, что наши маршруты станут работать излишне много, и в будущем это станет неудобно (сходи в одну модель, потом во вторую, обнови в третью и тому подобное).

Чтобы убрать строчку `async with async_session_maker() as session:` обычно используют отдельную функцию, типа такой:
```
# размещают в файле database.py

async def get_async_session():
    async with async_session_maker() as session:
        yield session
```
И потом в маршрутах получают сессию через Depends. Выглядит в маршрутах это так:

```
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.todo import ToDoFromDB, ToDoCreate
from app.db.database import get_async_session
from app.db.models import ToDo

todo_router = APIRouter(
    prefix="/todo",
    tags=["ToDo"]
)


@todo_router.get("/", response_model=list[ToDoFromDB])
async def get_todos(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(ToDo))
    return result.scalars().all()


@todo_router.post("/", response_model=ToDoFromDB)
async def create_todo(todo: ToDoCreate, session: AsyncSession = Depends(get_async_session)):
    new_todo = ToDo(**todo.model_dump())
    session.add(new_todo)
    await session.commit()
    await session.refresh(new_todo)
    return new_todo
```
Что также не сильно улучшает общую картину.
# Работа с базой данных через отдельный слой (паттерн репозиторий / паттерн DAO)
Следующим логичным шагом в развитии работы с БД через приложение становится вынесение работы с базой данных в отдельный слой.

Шаблон репозитория, также известный как шаблон DAO (data access object - объект доступа к данным), представляет собой шаблон проектирования, который абстрагирует логику доступа к данным от остальной части приложения. Такое разделение обеспечивает чистую и модульную архитектуру, упрощающую управление взаимодействиями с базой данных и переключение между различными реализациями хранилища данных, не затрагивая логику приложения более высокого уровня.

П.С. некоторые не согласятся с тем, что это одинаковые паттерны, но тут скорее важно понять концепцию.

## Ключевые концепции:
1. Разделение задач:

Без шаблона репозитория:
Логика доступа к данным разбросана по всему приложению.
Изменения в схеме базы данных могут потребовать обновления всей кодовой базы.
С шаблоном репозитория:
Логика доступа к данным централизована в репозитории, изолирована от остальной части приложения.
Изменения в схеме базы данных влияют только на репозиторий, сводя к минимуму влияние на приложение.
2. Абстракция:

Без шаблона репозитория:
Код приложения напрямую взаимодействует с API, специфичными для базы данных.
С шаблоном репозитория:
Код приложения взаимодействует с высокоуровневым интерфейсом репозитория.
Репозиторий обрабатывает детали, относящиеся к базе данных.
3. Гибкость:

Без шаблона репозитория:
Переключение на другую базу данных требует изменений во всем приложении.
С шаблоном репозитория:
Переключение баз данных предполагает обновление только реализации репозитория.
 
Давайте посмотрим на его имплементацию в наше приложение:
Для начала нам надо поправить нашу структуру, добавив в нее директорию repositories:
```
my_project
├── app
│   ├── api
│   │   ├── endpoints
│   │   │   ├── __init__.py
│   │   │   └── todo.py  
│   │   ├── schemas
│   │   │   ├── __init__.py
│   │   │   └── todo.py  
│   │   └── __init__.py
│   ├── core
│   │   ├── __init__.py
│   │   └── config.py  
│   ├── db
│   │   ├── __init__.py
│   │   ├── database.py  
│   │   └── models.py  
│   └── repositories  # создали директорию
│       ├── __init__.py  # сделали, как всегда, её пакетом
│       └── todo_repository.py  # и создали новый файл
├── .gitignore
├── .env
├── README.md
├── requirements.txt
└── main.py
```
Потом заполняем новый файл todo_repository.py:
```
from abc import ABC, abstractmethod

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.todo import ToDoCreate
from app.db.models import ToDo


class ToDoRepository(ABC):  # это абстрактный интерфейс нашего репозитория
    @abstractmethod
    async def get_todos(self) -> list[ToDo]:
        pass

    @abstractmethod
    async def create_todo(self, todo: ToDoCreate) -> ToDo:
        pass


class SqlAlchemyToDoRepository(ToDoRepository):  # это его конкретное исполнение для алхимии (можно сделать для peewee, pony и тд, легко поменять способ реализации)
    def __init__(self, session: AsyncSession):  # при инициализации принимает асинхронную сессию
        self.session = session

    # далее, по сути, код из эндпоинтов с предыдущего шага
    async def get_todos(self) -> list[ToDo]:
        result = await self.session.execute(select(ToDo))
        return result.scalars().all()

    async def create_todo(self, todo: ToDoCreate) -> ToDo:
        new_todo = ToDo(**todo.model_dump())
        self.session.add(new_todo)
        await self.session.commit()
        await self.session.refresh(new_todo)
        return new_todo

```
Можно назвать репозиторий, можно назвать DAO, кто-то именует сервисами, значения особого не имеет.

И последним шагом станет изменение нашего todo.py в папке endpoints:
```
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.todo import ToDoFromDB, ToDoCreate
from app.db.database import get_async_session
from app.repositories.todo_repository import ToDoRepository, SqlAlchemyToDoRepository

todo_router = APIRouter(
    prefix="/todo",
    tags=["ToDo"]
)


# тут нам нужна функция по инициализации ТуДу-репозитория (для уменьшения количества кода)
async def get_todo_repository(session: AsyncSession = Depends(get_async_session)) -> ToDoRepository:
    return SqlAlchemyToDoRepository(session)


# наши роуты стали значительно короче
@todo_router.get("/", response_model=list[ToDoFromDB])
async def get_todos(repo: ToDoRepository = Depends(get_todo_repository)):
    return await repo.get_todos()


# можно заметить, что оба роута зависят от общей функции получения репозитория, 
# которая зависит от сессий -> это пример цепочки инъекции зависимостей
@todo_router.post("/", response_model=ToDoFromDB)
async def create_todo(todo: ToDoCreate, repo: ToDoRepository = Depends(get_todo_repository)):
    return await repo.create_todo(todo)

```

Готово, можно тестировать. В целом это довольно распространенный пример работы с базой данных. Но у него есть пара недостатков:

- при наличии в БД нескольких моделей может возникнуть ситуация, что изменения в одной модели должны привести к изменениям в другой модели. Например заказ и его статус обработки. При создании заказа добавляется новая запись в базу данных, а потом нужно создать запись в модели "статус", в котором указать на каком этапе заказ, кто исполнитель по этому статусу, срок завершения этапа и что-то такое. При паттерне репозиторий у нас был бы поочередный вызов методов у двух моделей, а если какое-то из действий вызвало бы ошибку, то нам было бы не очень удобно удалять занесенную в БД запись. Усложнять в дальнейшем архитектуру можно существенно - потом добавить архив заказов, архив статусов и так далее...Сами представляете, как вырастает при этом вероятность ошибки сохранения/изменения/удаления какой-то части БД, что должно повлечь в коде "Галя, у нас отмена"...
- каждый маршрут на каждое обращение получает на фабрике новый объект сессии работы с базой данных. Так как объекты сессий разные, то может возникнуть конфликт (неконсистентность данных) в БД: один поток уже обновил данные, а второй ещё работает со старыми и потом вносит "обновленные" старые данные - то есть несогласованные коммиты.

Как с этим бороться будет на следующем шаге.

# Работа с базой данных через свой асинхронный контекстный менеджер (паттерн Unit of Work) через сервисы (контроллеры). Теория
## Unit of Work
Наверное последний уровень, необходимый для надежной работы с базой данных, это паттерн Unit of Work.

Давайте попробуем понять, чего мы хотим достичь, а потом уже будем смотреть как это реализовать. 

Паттерн Unit of Work часто используется в сочетании с шаблоном репозитория для управления координацией и отслеживанием изменений в базе данных. Unit of Work отвечает за обеспечение того, чтобы изменения, внесенные в ходе бизнес-транзакции, последовательно фиксировались или откатывались. Разницу можно посмотреть тут:



Как видно по картинке, unit of work (будем называть его uow для краткости) собирает в себе несколько репозиториев. То есть у нас есть некий общий интерфейс для работы с базой данных. Отличие от общего подхода в том, что контроллеры (про них попозже скажем) взаимодействуют с этой сущностью (uow), а не с репозиториями. 

Для наглядности, ещё одна иллюстрация:



На ней видно, что uow централизует в себе репозитории, а репозитории могут содержать (аггрегировать) несколько таблиц. 

Таким образом при этом паттерне мы можем уверенно соединить логику внесения изменений в БД (то есть централизовать коммиты). Это решит нашу проблему номер 1 из предыдущего шага. 

Проблему номер 2 из предыдущего шага можно решать с учётом следующих особенностей:

Реализация 1. Множественная инициализация uow. 

Реализация 2. Синглтон (единственный экземпляр) uow. 

- Если ваши сервисы работают независимо и им не нужно совместно использовать состояние, первый подход может быть более подходящим.
- Если ваши сервисы выигрывают от совместного использования одного и того же состояния и наличия общего "UnitOfWork", второй подход может быть предпочтительнее.

Во многих случаях первый подход (создание "UnitOfWork" в рамках зависимости каждой службы) обеспечивает четкое разделение задач и менее подвержен ошибкам. Однако второй подход (одноэлементный "UnitOfWork") может быть полезен, когда службам необходимо совместно использовать согласованное состояние, и возможность множественных подключений к базе данных не вызывает беспокойства.

В конечном счете, выбор зависит от конкретных потребностей и архитектуры вашего приложения.

Подробнее про паттерн uow тут, тут и тут. Настоятельно рекомендуем прочитать эти ссылки, там больше информации, которая поможет разобраться в принципах реализации паттерна uow.

## Сервисы (контроллеры) 
Теперь осталось обсудить сервисный подход. Их цель - снять бизнес-логику из маршрутов, чем повысить уровень абстракции и независимости. 

Внедрение сервисного уровня перед взаимодействием с UoW обеспечивает ряд преимуществ. Сервисный уровень инкапсулирует бизнес-логику, обеспечивая четкое разделение операций, специфичных для базы данных. Такая изоляция повышает тестируемость, позволяя легко имитировать (мокать) сервисы во время тестирования, обеспечивая согласованность преобразований данных и проверок. Сервисный уровень действует как абстракция, защищая слой API от изменений в базовых механизмах доступа к данным и повышая гибкость и адаптивность. Он также централизует обработку ошибок и управление исключениями, обеспечивая единообразные ответы и ведение журнала для различных бизнес-операций. Модульный и масштабируемый характер сервисов способствует созданию хорошо организованной и поддерживаемой базы кода, поддерживающей повторное использование в различных частях приложения.

Если кратко, наши эндпоинты дёргают метод сервиса, а уже сервис внутри обрабатывает запрос, дёргает методы uow по работе с разными (в т.ч. несколькими) моделями. Сервисы также дёргают методы других сервисов, выполняют подготовку данных (в т.ч. проверку, переформатирование и тп) для работы с БД. 

Например, у нас точка получи список todo, мы дергаем метод сервиса todo, а он проверяет: сходит в одну или несколько моделей в БД, соберёт из них тот формат, который должен вернуться клиенту и вернёт это в готовом виде в эндпоинт, который эти данные вернёт клиенту. Но также он мог бы теоретически сходить в БД и проверить существует ли такой юзер, дёрнуть метод сервиса прав доступа на наличие прав у этого юзера получения такого списка, дёрнуть метод внешнего сервиса (другого апи допустим) и получить оттуда доп.информацию для возврата и всё такое прочее. В общем сервис - это обособленная часть бизнес-логики. 

# Работа с базой данных через свой асинхронный контекстный менеджер (паттерн Unit of Work) через сервисы (контроллеры). Реализация
Давайте приступим ко внедрению.

Начнём со структуры проекта:
```
my_project
├── app
│   ├── api
│   │   ├── endpoints
│   │   │   ├── __init__.py
│   │   │   └── todo.py  # изменим содержимое
│   │   ├── schemas
│   │   │   ├── __init__.py
│   │   │   └── todo.py  # изменим содержимое
│   │   └── __init__.py
│   ├── core
│   │   ├── __init__.py
│   │   └── config.py
│   ├── db
│   │   ├── __init__.py
│   │   ├── database.py
│   │   └── models.py
│   ├── repositories
│   │   ├── __init__.py
│   │   ├── base_repository.py  # добавили (будем повышать уровень абстракции) 
│   │   └── todo_repository.py
│   ├── services  # добавили папку
│   │   ├── __init__.py
│   │   └── todo_service.py  # и файл
│   └── utils  # аналогично
│       ├── __init__.py
│       └── unitofwork.py  # и файл
├── .gitignore
├── .env
├── README.md
├── requirements.txt
└── main.py
```
Наша задача - добавить сервисы и uow.

Пока кратенько пробежимся по репозиториям.
Мы добавили файл base_repository.py следующего содержания:
```
from abc import ABC, abstractmethod

from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractRepository(ABC):
    @abstractmethod
    async def add_one(self, data: dict):
        raise NotImplementedError

    @abstractmethod
    async def find_all(self):
        raise NotImplementedError


class Repository(AbstractRepository):
    model = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_one(self, data: dict):
        stmt = insert(self.model).values(**data).returning(self.model)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def find_all(self):
        result = await self.session.execute(select(self.model))
        return result.scalars().all()
```
Мы сказали, что у нас есть абстрактный репозиторий, в котором точно должно быть 2 метода - добавь один и найди все. И сделали его конкретную реализацию (под алхимию).

Обратите внимание, что мы повысили уровень абстракции репозитория, указав, что у репозитория есть некая модель. И все запросы к базе данных обезличены (вставь в модель некие данные: словарь, вернув модель). Stmt сокращение от statement - читайте "запрос к БД", кто-то пишет query, не суть принципиально. Или другой запрос - выбери модель (вернёт все поля). Если моделей было бы 5, то на месте model была бы каждая модель, и методы были бы универсальны для них всех (найди, добавь) - и работало бы по всем 5 таблицам в базе данных. Это очень удобно. Дальше в комментариях к итговому проекту имеется пример репозитория с довольно большим количеством общих CRUD.

Теперь наш todo_repository.py очень краток:
```
from app.db.models import ToDo
from app.repositories.base_repository import Repository


class ToDoRepository(Repository):
    model = ToDo
```
Все остальные методы у него есть от родительского класса. Это соответствует SOLID.

Теперь рассмотрим uow.
Заполняем файл unitofwork.py следующим содержимым:
```
from abc import ABC, abstractmethod

from app.db.database import async_session_maker
from app.repositories.todo_repository import ToDoRepository


class IUnitOfWork(ABC):
    todo: ToDoRepository

    @abstractmethod
    def __init__(self):
        ...

    @abstractmethod
    async def __aenter__(self):
        ...

    @abstractmethod
    async def __aexit__(self, *args):
        ...

    @abstractmethod
    async def commit(self):
        ...

    @abstractmethod
    async def rollback(self):
        ...


class UnitOfWork(IUnitOfWork):
    def __init__(self):
        self.session_factory = async_session_maker

    async def __aenter__(self):
        self.session = self.session_factory()

        self.todo = ToDoRepository(self.session)

    async def __aexit__(self, *args):
        await self.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
```
Тут сложность будет побольше:

- Абстрактный uow будет является интерфейсом. В нем будет список репозиториев, которые должны содержаться в конкретной реализации, и методы. Методы такие: это асинхронный вход и выход (uow станет нашим асинхронными контекстным менеджером) - aenter и aexit. Плюс нам потребуется конструктор класса и методы коммит и ролбэк. Именно последние два позволят централизованно управлять коммитами в нашу БД (закоммитить можно будет только внутри контекста uow, а вне контекста - нельзя). Это гарантирует нам централизованность.
- Конкретный uow в конструкторе принимает наш создатель сессий. При входе в контекст мы получаем сессию и инициализируем наши репозитории (в нашем случае ToDo-репозиторий), передавая в него эту сессию. При выходе из контекста мы делаем rollback (то есть все незакомиченные изменения откатываются) и закрываем сессию - если ошибка произойдёт внутри контекста uow, то все изменения откатятся, а сессия закроется, что снимает с нас головную боль. Ну и методы коммит и ролбэк просто уменьшают количество кода нам самим.

Теперь время сервисов

Заполним todo_service.py так:
```
from app.api.schemas.todo import ToDoCreate, ToDoFromDB
from app.utils.unitofwork import IUnitOfWork


class ToDoService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def add_todo(self, todo: ToDoCreate) -> ToDoFromDB:
        todo_dict: dict = todo.model_dump()  # подготовка данных для внесения в БД
        async with self.uow:  # вход в контекст (если выбьет с ошибкой, то изменения откатятся) 
            todo_from_db = await self.uow.todo.add_one(todo_dict)
            todo_to_return = ToDoFromDB.model_validate(todo_from_db)  # обработка полученных данных из БД для их возврата - делаем модель пидантик
            await self.uow.commit()  # это самый важный кусок кода, до этого коммита можно записать данные в 50 моделей, но если кто-то вылетит с ошибкой, все изменения откатятся! Если код дошёл сюда, то все прошло окей! 
            return todo_to_return

    async def get_todos(self) -> list[ToDoFromDB]:
        async with self.uow:
            todos: list = await self.uow.todo.find_all()
            return [ToDoFromDB.model_validate(todo) for todo in todos]
```
Наш сервис todo будет обслуживать всю группу роутов todo. В нем пока два метода, но потом их может стать больше. Он принимает наш uow и потом в методах с ним работает. В данном варианте у нас всего одна модель, но в перспективе сервис может дёргать разные репозитории по-очереди, и потом централизованно коммитить. Также сервис выполняет предварительную подготовку данных для добавления и последующую обработку данных после получения из БД.

Пара слов про model_validate: это так можно сделать из объекта базы данных алхимии объект пидантика. Чтобы оно работало, нам надо доработать наши схемы:
```
import datetime

from pydantic import BaseModel, ConfigDict


class ToDoCreate(BaseModel):
    description: str
    completed: bool | None = False


class ToDoFromDB(ToDoCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime.datetime
```
Строчка `model_config = ConfigDict(from_attributes=True)` укажет пидантик-модели, что в него может поступить не только словарь, но и объект. Модель пройдётся по атрибутами модели и заберёт из них значения (энумирация).

И в завершение - наши роуты.
Давайте теперь взглянем на последнюю часть - на маршруты:
```
from fastapi import APIRouter, Depends

from app.api.schemas.todo import ToDoFromDB, ToDoCreate
from app.services.todo_service import ToDoService
from app.utils.unitofwork import UnitOfWork, IUnitOfWork


todo_router = APIRouter(
    prefix="/todo",
    tags=["ToDo"]
)


async def get_todo_service(uow: IUnitOfWork = Depends(UnitOfWork)) -> ToDoService:
    return ToDoService(uow)


@todo_router.post("/todos/", response_model=ToDoFromDB)
async def create_todo(todo_data: ToDoCreate, todo_service: ToDoService = Depends(get_todo_service)):
    return await todo_service.add_todo(todo_data)


@todo_router.get("/todos/", response_model=list[ToDoFromDB])
async def get_todos(todo_service: ToDoService = Depends(get_todo_service)):
    return await todo_service.get_todos()
```
Тут мы создали функцию по получению Todo-сервиса, которая через зависимость получает uow и передаёт его в сервис. Дальше в роутах мы уже работаем с методами нашего сервиса (контроллера), абсолютно не задумываясь как там встроена бизнес-логика.

На этом наверное всё.

Полный код проекта находится по ссылке https://github.com/Cheater121/sqlalchemy_postgres_fastapi/tree/master. 

Можете сравнить его с другим проектом и самостоятельно в этом всем покопаться. Если память не изменяет, во втором проекте модельки с отношениями (связаны), тут эта информация не давалась, так как ухудшилось бы восприятие.

Надеемся, что теперь у вас сложилось понимание о том, как выстроить работу FastAPI с SQLAlchemy и PostgreSQL и у вас получится самостоятельно выполнить итоговые проекты. 