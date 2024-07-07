# Тут мы сначала объявили модель `Image`, и далее в объекте `Item` её вложили. После этого передали эту модель в соответствующую функцию, обрабатывающую PUT-запрос. Соответственно FastAPI будет ожидать такой входящий JSON:

# {
#     "name": "Foo",
#     "description": "The pretender",
#     "price": 42.0,
#     "tax": 3.2,
#     "tags": ["rock", "metal", "bar"],
#     "image": {
#         "url": "http://example.com/baz.jpg",
#         "name": "The Foo live"
#     }
# }
# Таким образом FastAPI позволяет настраивать валидируемые схемы данных любым удобным для нас способом, что повышает общую гибкость приложения.
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Image(BaseModel):
    url: str
    name: str


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()
    image: Image | None = None


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    results = {"item_id": item_id, "item": item}
    return results
