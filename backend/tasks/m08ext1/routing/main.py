from fastapi import FastAPI
from electronics import electronicsroute
from gadgets import gadgetsroute


app = FastAPI()
app.include_router(electronicsroute, prefix="/electronics")
app.include_router(gadgetsroute, prefix="/gadgets")


@app.get("/")
def index():
    return "Welcome to the Electronics Store"
