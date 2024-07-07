from fastapi import FastAPI

# создаём суб-приложение
api_v1_app = FastAPI()


# определяем роут в суб-приложении
@api_v1_app.get("/sub/")
def read_sub():
    return {"message": "This is a sub-application route."}
