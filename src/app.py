import os
import requests
from flask import Flask, request, render_template
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime
import logging

load_dotenv()

app = Flask(__name__)

# MongoDB connection
client = MongoClient(os.getenv("MONGO_URI"))
db = client["History"]
collection = db["Requests"]

# Set up logging
logging.basicConfig(level=logging.DEBUG)


def save_request_to_db(city, temperature):
    current_time = datetime.now()
    request_data = {
        "time": current_time,
        "city": city,
        "temperature": temperature,
    }
    collection.insert_one(request_data)


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
        logging.error(
            "Failed to fetch weather data. Status code: %s", response.status_code)
        return None


@app.route("/", methods=["GET", "POST"])
def main():
    error_message = None
    temperature = None
    description = None

    # Fetch previous requests from MongoDB
    previous_requests = list(collection.find().sort("time", -1))

    if request.method == "POST":
        city = request.form.get("city", "")
        if city:
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
                        save_request_to_db(city, temperature)
                else:
                    error_message = "Failed to fetch weather data from API"
            else:
                error_message = "Failed to get coordinates for the city"

    return render_template("index.html", error_message=error_message, temperature=temperature, description=description, previous_requests=previous_requests)


if __name__ == '__main__':
    app.run(debug=True)
