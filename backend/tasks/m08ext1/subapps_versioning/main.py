from fastapi import FastAPI
from api_v1 import api_v1_app

# создаём главное FastAPI приложение
app = FastAPI()

# монтируем суб-приложение в основное приложение
app.mount("/v1", api_v1_app)


# создаём обычный роут в главном приложении
@app.get("/")
def root():
    return {"message": "Hello from main app"}
