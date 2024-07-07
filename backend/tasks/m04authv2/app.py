from fastapi import FastAPI
from auth import Auth
from db import RedisDB
from routes import authentication

users_db = RedisDB(host="127.0.0.1", decode=True)
app = FastAPI(title="RBAC_JWT")
auth_handler = Auth()

# app.include_router(other, prefix="")
app.include_router(authentication, prefix="")
