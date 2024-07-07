from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

import m04authv2.app as app
from m04authv2.models import AuthModel, Up

authentication = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@authentication.post("/signup")
async def signup(user: AuthModel):
    """Получаем данные для регистрации аккаунта. В случае успеха - пишем в БД.
    Если, аккаунт первый в БД, то, он получает роль  'admin'"""
    if app.users_db.load_kv(user.username, "username"):
        return {"message": "Аккаунт уже существует!"}
    try:
        hashed_password = app.auth_handler.encode_password(user.password)
        if app.users_db.get_size():
            data = {
                "username": user.username,
                "password": hashed_password,
                "role": "guest",
            }
        else:
            data = {
                "username": user.username,
                "password": hashed_password,
                "role": "admin",
            }
        app.users_db.save_record(data)
        app.users_db.write_db()
        return {"message": "Аккаунт зарегистрирован."}
    except:
        return {"message": "Неудачная регистрация аккаунта."}


@authentication.post("/login")
async def login(user: OAuth2PasswordRequestForm = Depends()):
    """Получаем из формы данные (логин, пароль). Если всё валидно выдаём токен.
    Fastapi предоставляет специальный dependency класс OAuth2PasswordRequestForm,
    который заставляет конечную точку ожидать два поля username и password.
    """
    username = app.users_db.load_kv(user.username, "username")
    if username == None:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    passwd = app.users_db.load_kv(user.username, "password")
    if not app.auth_handler.verify_password(user.password, passwd):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный пароль.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = app.auth_handler.encode_token(username)
    return {"access_token": token}


@authentication.post("/protected_resource")
async def protect_resource(token: str = Depends(oauth2_scheme)):
    """Роль admin может просмотреть из БД логины и роли аккаунтов
    Роль user может просмотреть из БД логины аккаунтов
    Роль guest - доступ запрещён.
    """
    username = app.auth_handler.decode_token(token)
    role = app.users_db.load_kv(username, "role")
    if role == "admin":
        db_query = app.users_db.all_key_value()
        return {
            "message": "Доступ разрешен.",
            "current user": username,
            "all user": db_query,
        }
    if role == "user":
        db_query = [{"username": i["username"]} for i in app.users_db.all_key_value()]
        return {
            "message": "Доступ разрешен.",
            "current user": username,
            "all user": db_query,
        }

    raise HTTPException(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        detail="Access Dieaned!!!",
        headers={"WWW-Authenticate": "Bearer"},
    )


@authentication.post("/role_up")
async def role_up(user_up: Up = None, token: str = Depends(oauth2_scheme)):
    """Повышение роли аккаунта - из guest в user.
    Доступ только у роли admin.
    """
    usr = user_up.user_up
    username = app.auth_handler.decode_token(token)
    role = app.users_db.load_kv(username, "role")
    if role == "admin":
        role_user = app.users_db.load_kv(usr, "role")
        if role_user == "guest":
            update = {"username": usr, "role": "user"}
            app.users_db.save_record(update)
            app.users_db.write_db()
            return {
                "message": f"Доступ разрешен.",
                "current user": username,
                "up": True,
            }
        raise HTTPException(
            status_code=status.HTTP_304_NOT_MODIFIED,
            detail="Пользователь не существует, либо не возможно изменить роль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    raise HTTPException(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        detail="Access Dieaned!!!",
        headers={"WWW-Authenticate": "Bearer"},
    )
