import os
from dotenv import load_dotenv, find_dotenv


class Configuration:
    load_dotenv(find_dotenv())
    secret_key = (
        os.environ.get("APP_SECRET_STRING")
        or "!#!my123super123mega123secret123string!#!"
    )
    salt = "salt#_#"
    ALGORITHM = "HS256"
    EXP_DAYS = 0
    EXP_MINUTES = 10
