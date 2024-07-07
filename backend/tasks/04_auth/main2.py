from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
)  # для реквест-формы нам нужно установить доп. библиотеку командой pip install python-multipart
from pydantic import BaseModel
import jwt
from typing import Optional, Annotated

"""тут работаем с библиотекой PyJWT, 
но в реальной жизни вы скорее всего предпочтете 'python-jose', которая чуть шире PyJWT и рекомендуется самими FastAPI
"""

app = FastAPI()

# Секретный ключ для подписи и верификации токенов JWT
SECRET_KEY = "mysecretkey"  # тут мы в реальной практике используем что-нибудь вроде команды Bash (Linux) 'openssl rand -hex 32', и храним очень защищенно
ALGORITHM = "HS256"  # плюс в реальной жизни мы устанавливаем "время жизни" токена

# Пример информации из БД
USERS_DATA = {
    "admin": {"username": "admin", "password": "adminpass", "role": "admin"},
    "user": {"username": "user", "password": "userpass", "role": "user"},
}  # в реальной БД мы храним только ХЭШИ паролей (можете прочитать про библиотеку, к примеру, 'passlib') + соль (известная только нам добавка к паролю)

# OAuth2PasswordBearer для авторизации по токену
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Модель User для аутентификации (если делали задание по JWT, то тут добавляем только роль)
class User(BaseModel):
    username: str
    password: str
    role: Optional[str] = None


# Функция для создания JWT токена
def create_jwt_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


# Функция получения User'а по токену - это скорее всего была самая сложная часть в предыдущем задании
def get_user_from_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM]
        )  # декодируем токен
        return payload.get(
            "sub"
        )  # тут мы идем в полезную нагрузку JWT-токена и возвращаем утверждение о юзере (subject); обычно там еще можно взять "iss" - issuer/эмитент, или "exp" - expiration time - время 'сгорания' и другое, что мы сами туда кладем
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Функция для получения пользовательских данных на основе имени пользователя
def get_user(username: str):
    if username in USERS_DATA:
        user_data = USERS_DATA[username]
        return User(**user_data)
    return None


# Роут для получения JWT-токена (так работает логин)
@app.post("/token/")
def login(
    user_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):  # тут логинимся через форму
    user_data_from_db = get_user(user_data.username)
    if user_data_from_db is None or user_data.password != user_data_from_db.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {
        "access_token": create_jwt_token({"sub": user_data.username})
    }  # тут мы добавляем полезную нагрузку в токен, и говорим, что "sub" содержит значение username


# Защищенный роут для админов, когда токен уже получен
@app.get("/admin/")
def get_admin_info(current_user: str = Depends(get_user_from_token)):
    user_data = get_user(current_user)
    if user_data.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
    return {"message": "Welcome Admin!"}


# Защищенный роут для обычных пользователей, когда токен уже получен
@app.get("/user/")
def get_user_info(current_user: str = Depends(get_user_from_token)):
    user_data = get_user(current_user)
    if user_data.role != "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
    return {"message": "Hello User!"}
