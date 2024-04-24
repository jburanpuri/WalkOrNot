import requests
import os
import logging


def get_weather_data(city):
    api_key = os.getenv("API_KEY")

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        logging.error("Failed to fetch weather data. Status code: " +
                      str(response.status_code) + ", Response: " + response.text)
        return None
