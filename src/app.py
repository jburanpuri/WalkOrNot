from flask import Flask, request, jsonify, render_template
import requests
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from src.messages import send_message, setup_queue
import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)

# MongoDB setup
client = MongoClient(os.getenv('MONGO_URI'))
db = client.walkornot
history = db.history


def data_analyzer(current):
    suggestions = []

    feels_like = current['main']['feels_like'] - 273.15
    visibility = current['visibility']
    cloudiness = current['clouds']['all']
    temp_min = current['main']['temp_min'] - 273.15
    temp_max = current['main']['temp_max'] - 273.15
    conditions = current['weather'][0]['main']

    facts = [
        "Feels-like temperature: {:.1f}°C".format(feels_like),
        "visibility: {} meters".format(visibility),
        "minimum temperature: {:.1f}°C".format(temp_min),
        "maximum temperature: {:.1f}°C".format(temp_max),
        "weather conditions: {} (cloudiness: {}%)".format(
            conditions, cloudiness)
    ]

    if 'Rain' in current['weather'][0]['main']:
        suggestions.append(
            "Consider wearing a raincoat or carrying an umbrella.")
    if temp_min < 10:
        suggestions.append(
            "It's quite chilly, so consider wearing a jacket or sweater.")

    if visibility > 10000:
        suggestions.append(
            "Visibility is good, so you can enjoy the view.")

    if cloudiness > 70:
        suggestions.append(
            "It's cloudy. Either its vibes or you stay inside.")

    if suggestions == []:
        suggestions.append("The weather is nice. Enjoy your walk!")

    analysis_response = {
        'facts': facts,
        'suggestions': " ".join(suggestions)
    }

    return analysis_response


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/check_weather', methods=['POST'])
def check_weather():
    city = request.form['city']
    geo_url = "https://maps.googleapis.com/maps/api/geocode/json?address={}&key={}".format(
        city, os.getenv('GEOCODING_API_KEY'))
    geo_resp = requests.get(geo_url).json()
    if 'results' not in geo_resp or not geo_resp['results']:
        return jsonify({'error': 'Geocode data not found for the specified city'}), 404

    lat = geo_resp['results'][0]['geometry']['location']['lat']
    lon = geo_resp['results'][0]['geometry']['location']['lng']

    weather_url = "https://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}".format(
        lat, lon, os.getenv('API_KEY'))
    weather_resp = requests.get(weather_url).json()

    if 'main' not in weather_resp or 'weather' not in weather_resp:
        return jsonify({'error': 'Weather data not found'}), 404

    analysis = data_analyzer(weather_resp)

    document = {
        'city': city,
        'feels_like': round(weather_resp['main']['feels_like'] - 273.15, 1),
        'humidity': weather_resp['main']['humidity'],
        'visibility': weather_resp['visibility'],
        'cloudiness': weather_resp['clouds']['all'],
        'temp_min': round(weather_resp['main']['temp_min'] - 273.15, 1),
        'temp_max': round(weather_resp['main']['temp_max'] - 273.15, 1),
        'weather_main': weather_resp['weather'][0]['main'],
        'facts': analysis['facts'],
        'suggestions': analysis['suggestions'],
        'timestamp': datetime.datetime.now()
    }

    history.insert_one(document)

    response_data = {
        'city': city,
        'feels_like': round(weather_resp['main']['feels_like'] - 273.15, 1),
        'humidity': weather_resp['main']['humidity'],
        'visibility': weather_resp['visibility'],
        'cloudiness': weather_resp['clouds']['all'],
        'temp_min': round(weather_resp['main']['temp_min'] - 273.15, 1),
        'temp_max': round(weather_resp['main']['temp_max'] - 273.15, 1),
        'weather_main': weather_resp['weather'][0]['main'],
        'facts': analysis['facts'],
        'suggestions': analysis['suggestions']
    }

    return jsonify(response_data)


@app.route('/history', methods=['GET'])
def history_page():
    return render_template('history.html')


@app.route('/history_data', methods=['GET'])
def get_history():
    records = list(history.find({}, {'_id': 0}))
    return jsonify(records)


if __name__ == '__main__':
    setup_queue()
    app.run(debug=True)
