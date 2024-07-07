from pydantic import BaseModel, Field


class AuthModel(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    password: str = Field(min_length=5, max_length=30)


class Up(BaseModel):
    user_up: str
