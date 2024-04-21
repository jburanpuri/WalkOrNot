import os
import requests
from flask import Flask, request, render_template
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

previous_requests = []


def get_coordinates(city):
    api_key = os.getenv("GEOCODING_API_KEY")
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": city, "key": api_key}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data and data.get("results"):
            location = data["results"][0]["geometry"]["location"]
            return location.get("lat"), location.get("lng")
    return None, None


def get_weather_data(lat, lon):
    api_key = os.getenv("API_KEY")
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"lat": lat, "lon": lon, "appid": api_key, "units": "metric"}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None


@app.route("/", methods=["GET", "POST"])
def main():
    error_message = None
    temperature = None
    description = None

    if request.method == "POST":
        city = request.form.get("city", "")
        if city:
            previous_requests.append(city)
            lat, lon = get_coordinates(city)
            if lat and lon:
                weather_data = get_weather_data(lat, lon)
                if weather_data:
                    temperature = weather_data.get("main", {}).get("temp")
                    description = weather_data.get("weather", [{}])[
                        0].get("description")
                    if not temperature or not description:
                        error_message = "Failed to fetch weather data"
                else:
                    error_message = "Failed to fetch weather data from API"
            else:
                error_message = "Failed to get coordinates for the city"

    return render_template("index.html", error_message=error_message, temperature=temperature, description=description, previous_requests=previous_requests)


if __name__ == '__main__':
    app.run(debug=True)
