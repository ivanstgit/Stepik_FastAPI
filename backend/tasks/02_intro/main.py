import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()


@app.get("/", response_class=FileResponse)
async def root_html():
    return os.path.join(BASE_DIR, "index.html")


class Numbers(BaseModel):
    num1: int | float
    num2: int | float


@app.post("/calculate/")
async def calculate(numbers: Numbers) -> dict[str, int | float]:
    result = numbers.num1 + numbers.num2
    return {"result": result}
