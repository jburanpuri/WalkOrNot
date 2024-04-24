import os
import requests
from flask import Flask, request, render_template
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime
import logging
from messages import send_to_queue


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


def get_weather_data(city):
    api_key = os.getenv("API_KEY")
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": api_key, "units": "metric"}
    response = requests.get(url, params=params)
    print("API Response:", response.json())  # Debug print
    if response.status_code == 200:
        return response.json()
    else:
        logging.error("Failed to fetch weather data. Status code: %s, Response: %s",
                      response.status_code, response.text)
        return None


@app.route("/history")
def history():
    previous_requests = list(collection.find(
        {}, {"_id": 0, "time": 1, "city": 1, "temperature": 1}).sort("time", -1))
    return render_template("history.html", previous_requests=previous_requests)


@app.route("/", methods=["GET", "POST"])
def main():
    error_message = None
    previous_requests = list(collection.find().sort("time", -1))

    if request.method == "POST":
        city = request.form.get("city", "")
        if city:
            send_to_queue('weather_requests', {'city': city})
            message = "Request sent for processing, check back shortly for results."
            return render_template("index.html", message=message, previous_requests=previous_requests)
        else:
            error_message = "Please enter a city name"
            return render_template("index.html", error_message=error_message, previous_requests=previous_requests)

    return render_template("index.html", previous_requests=previous_requests)


if __name__ == '__main__':
    app.run(debug=True)
