from fastapi import APIRouter

electronicsroute = APIRouter()


@electronicsroute.get("/info")
def electronics():
    return {
        "detail": "This electronics info is from the electronics APIRouter",
        "name": "Electronics XYZ",
        "brand": "ABC Electronics",
    }
