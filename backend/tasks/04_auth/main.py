from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .dataclasses import models

app = FastAPI()


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


SECRET_KEY = "dba749b064fa8502475b7bd8b31b81d2cb20a34fbfee762ba4ba9c09093c799a"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(username: str, db: Session = Depends(get_db)):
    return db.query(models.User).filter(models.User.username == username).first()


def authenticate_user(db, username: str, password: str):
    user = get_user(username, db)
    if not user or not verify_password(password, user.password):
        return False
    return True


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@app.post("/login")
async def login_for_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    username = form_data.username
    password = form_data.password

    if not authenticate_user(db, username, password):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/protected_resource")
async def protected_resource(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.DecodeError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"message": "Access granted to protected resource"}
