from flask import Flask, request, jsonify, render_template
import requests
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from messages import send_message, setup_queue

# Load environment variables
load_dotenv()

app = Flask(__name__)

# MongoDB setup
client = MongoClient(os.getenv('MONGO_URI'))
db = client.walkornot
history = db.history


def data_analyzer(temperature, condition):
    if temperature > 10 and ('rain' not in condition.lower()):
        return "Good day for a walk"
    else:
        return "Not a good day for a walk"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/check_weather', methods=['POST'])
def check_weather():
    city = request.form['city']
    geo_url = "https://maps.googleapis.com/maps/api/geocode/json?address={}&key={}".format(
        city, os.getenv('GEOCODING_API_KEY'))
    geo_resp = requests.get(geo_url).json()
    lat = geo_resp['results'][0]['geometry']['location']['lat']
    lon = geo_resp['results'][0]['geometry']['location']['lng']

    weather_url = "https://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}&units=metric".format(
        lat, lon, os.getenv('API_KEY'))
    weather_resp = requests.get(weather_url).json()
    temperature = weather_resp['main']['temp']
    condition = weather_resp['weather'][0]['main']

    analysis = data_analyzer(temperature, condition)

    # Save to MongoDB
    history.insert_one({'city': city, 'temperature': temperature,
                       'condition': condition, 'analysis': analysis})

    # Send message to queue
    send_message({'city': city, 'temperature': temperature,
                 'condition': condition, 'analysis': analysis})

    return jsonify({'city': city, 'temperature': temperature, 'condition': condition, 'analysis': analysis})


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
