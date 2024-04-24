from flask import render_template
from flask import jsonify
from flask import Flask, request, render_template
from threading import Thread
from messages import start_consumer, process_weather_request
from database import Database
from messages import send_to_queue

# Create the Flask application
app = Flask(__name__)

# Initialize the database connection
db = Database()

# Define the route for the homepage ("/") and the history ("/history")


@app.route("/", methods=["GET", "POST"])
def main():
    if request.method == "POST":
        city = request.form.get("city", "")
        if city:
            send_to_queue('weather_requests', {'city': city})
            return jsonify({"message": "Request sent for processing, check back shortly for results."})
        else:
            return jsonify({"error_message": "Please enter a city name"})

    previous_requests = db.get_previous_requests()
    return render_template("index.html", previous_requests=previous_requests)


@app.route("/history")
def history():
    previous_requests = db.get_previous_requests()
    return render_template("history.html", previous_requests=previous_requests)


if __name__ == '__main__':
    consumer_thread = Thread(target=start_consumer, args=(
        'weather_requests', process_weather_request))
    consumer_thread.start()
    app.run(debug=True)
