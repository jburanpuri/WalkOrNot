from threading import Lock
from flask import Flask, request, render_template, json, Response
import logging
from messages import send_to_queue, start_consumer
from database import Database
from weather_service import get_weather_data
import threading
import time
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
db = Database()

# Lock for thread-safe operations on data_store
data_lock = Lock()
data_store = {}


@app.route("/", methods=["GET", "POST"])
def main():
    if request.method == "POST":
        city = request.form.get('city')
        send_to_queue('weather_requests', {'city': city})
        with data_lock:
            data_store['city'] = city
        return render_template('loading.html')
    return render_template('index.html')


@app.route("/history")
def history():
    previous_requests = db.get_previous_requests()
    return render_template("history.html", previous_requests=previous_requests)


@app.route('/stream')
def stream():
    def event_stream():
        while True:
            with data_lock:
                if 'temperature' in data_store:
                    yield f"data: {{'city': '{data_store['city']}', 'temperature': '{data_store['temperature']}'}}\n\n"
                    data_store.clear()
            time.sleep(1)
    return Response(event_stream(), mimetype='text/event-stream')


def process_weather_response(ch, method, properties, body):
    try:
        response = json.loads(body)
        city = response['city']
        weather_data = get_weather_data(city)
        if weather_data:
            temperature = weather_data['main']['temp']
            db.save_request_to_db(city, temperature)
            with data_lock:
                data_store['temperature'] = temperature
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            logging.error("Failed to fetch weather data for city: " + city)
    except Exception as e:
        logging.error(f"An error occurred: {e}")


def start_message_consumer():
    start_consumer('weather_responses', process_weather_response)


if __name__ == '__main__':
    consumer_thread = threading.Thread(
        target=start_message_consumer, daemon=True)
    consumer_thread.start()
    app.run(debug=True)
