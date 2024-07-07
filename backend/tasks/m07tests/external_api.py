import requests


def fetch_data_from_api():
    response = requests.get("https://api.example.com/data")
    if response.status_code == 200:
        return response.json()
    else:
        return None


def process_data(data):
    # какая-то логика обработки данных
    new_data = {}
    for key, value in data.items():
        new_data[key.upper()] = value.upper()
    return new_data
