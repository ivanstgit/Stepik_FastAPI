from fastapi import (
    FastAPI,
    HTTPException,
    Request,
    status,
)  # ДОБАВИЛИ импорт статусов, чтобы в тексте статус коды понятнее читались
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel


app = FastAPI()


# не изменяли
class ItemsResponse(BaseModel):
    item_id: int


# не изменяли
class CustomExceptionModel(BaseModel):
    status_code: int
    er_message: str
    er_details: str


# не изменяли
class CustomException(HTTPException):
    def __init__(self, detail: str, status_code: int, message: str):
        super().__init__(status_code=status_code, detail=detail)
        self.message = message


# не изменяли
@app.exception_handler(CustomException)
async def custom_exception_handler(
    request: Request, exc: CustomException
) -> JSONResponse:
    error = jsonable_encoder(
        CustomExceptionModel(
            status_code=exc.status_code, er_message=exc.message, er_details=exc.detail
        )
    )
    return JSONResponse(status_code=exc.status_code, content=error)


# ДОБАВИЛИ много мета-информации для описания нашей конечной точки
@app.get(
    "/items/{item_id}/",
    response_model=ItemsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Items by ID.",
    description="The endpoint returns item_id by ID. If the item_id is 42, an exception with the status code 404 is returned.",
    responses={
        status.HTTP_200_OK: {"model": ItemsResponse},
        status.HTTP_404_NOT_FOUND: {
            "model": CustomExceptionModel
        },  # вот тут применяем схемы ошибок пидантика
    },
)
async def read_item(item_id: int):
    if item_id == 42:
        raise CustomException(
            detail="Item not found",
            status_code=404,
            message="You're trying to get an item that doesn't exist. Try entering a different item_id.",
        )
    return ItemsResponse(item_id=item_id)
