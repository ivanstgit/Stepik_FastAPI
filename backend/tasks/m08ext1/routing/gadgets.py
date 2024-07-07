from fastapi import APIRouter

gadgetsroute = APIRouter()


@gadgetsroute.get("/info")
def gadgets():
    return {
        "detail": "This gadgets info is from the gadgets APIRouter",
        "name": "Cool Gadget",
        "manufacturer": "Gadget Co.",
    }
