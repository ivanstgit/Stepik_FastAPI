from fastapi import FastAPI

from external_api import fetch_data_from_api, process_data

app = FastAPI()


def get_and_process_data():
    data = fetch_data_from_api()
    if data:
        return process_data(data)
    else:
        return None


@app.get("/sum/")
def calculate_sum(a: int, b: int):
    return {"result": a + b}
