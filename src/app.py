from threading import Lock
from flask import Flask, request, render_template, json, Response
import logging
from weather_service import get_weather_data
import threading
import time
from dotenv import load_dotenv
from messages import send_to_queue, start_consumer
from database import Database


load_dotenv()

app = Flask(__name__)
db = Database()

data_lock = Lock()
data_store = {}


@app.route("/", methods=["GET", "POST"])
def main():
    if request.method == "POST":
        city = request.form.get('city')
        send_to_queue('weather_requests', {'city': city})
        with data_lock:
            data_store['city'] = city
            data_store['status'] = "Loading weather data..."
        return render_template('index.html')
    return render_template('index.html')


@app.route("/history")
def history():
    previous_requests = db.get_previous_requests()
    return render_template("history.html", previous_requests=previous_requests)


@app.route('/stream')
def stream():
    def event_stream():
        while True:
            time.sleep(1)  # Small delay to avoid tight loop
            with data_lock:
                if 'temperature' in data_store and 'decision' in data_store:
                    response_data = {
                        'city': data_store['city'],
                        'temperature': data_store['temperature'],
                        'decision': data_store['decision']
                    }
                    yield f"data: {json.dumps(response_data)}\n\n"
                    data_store.clear()
                elif 'status' in data_store:
                    yield f"data: {json.dumps({'status': data_store['status']})}\n\n"
    return Response(event_stream(), mimetype='text/event-stream')


def process_weather_response(ch, method, properties, body):
    try:
        response = json.loads(body)
        city = response['city']
        weather_data = get_weather_data(city)
        if weather_data:
            temperature = weather_data['main']['temp']
            db.save_request_to_db(city, temperature)
            decision = "It's a good day for a walk!" if temperature > 10 and temperature < 30 else "Not a great day for a walk."
            with data_lock:
                data_store.update(
                    {'temperature': temperature, 'decision': decision})
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            with data_lock:
                data_store['status'] = "Failed to fetch data."
    except Exception as e:
        logging.error(f"An error occurred: {e}")


def start_message_consumer():
    start_consumer('weather_responses', process_weather_response)


if __name__ == '__main__':
    threading.Thread(target=start_message_consumer, daemon=True).start()
    app.run(debug=True)
