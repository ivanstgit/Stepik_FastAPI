from fastapi import HTTPException
import jwt  # для кодирования токена
from passlib.context import CryptContext  # для хеширования пароля
from datetime import datetime, timedelta

from config import Configuration


class Auth:
    hasher = CryptContext(schemes=["bcrypt"])
    config = Configuration()

    def encode_password(self, password):
        """
        Хешируем пароль и возвращаем хеш.
        """
        return self.hasher.hash(password + self.config.salt)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Сравниваем полученный пароль с хешем.
        Если совпадает, выдаём True
        """
        return self.hasher.verify(plain_password + self.config.salt, hashed_password)

    def encode_token(self, username):
        """Кодируем токен"""
        payload = {
            "exp": datetime.utcnow()
            + timedelta(days=self.config.EXP_DAYS, minutes=self.config.EXP_MINUTES),
            "iat": datetime.utcnow(),
            "scope": "access_token",
            "sub": username,
        }
        return jwt.encode(payload, self.config.secret_key, self.config.ALGORITHM)

    def decode_token(self, token):
        """
        Декодируем токен.
        """
        try:
            payload = jwt.decode(token, self.config.secret_key, self.config.ALGORITHM)
            if payload["scope"] == "access_token":
                return payload["sub"]
            raise HTTPException(
                status_code=401,
                detail="Неверная область действия токена",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401,
                detail="Срок действия токена истек",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=401,
                detail="Недействительный токен",
                headers={"WWW-Authenticate": "Bearer"},
            )
