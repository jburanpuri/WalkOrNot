import json
from messages import create_connection, start_consumer


def process_weather_data(ch, method, properties, body):
    data = json.loads(body)
    temp = data['main']['temp']
    conditions = ', '.join([weather['description']
                           for weather in data['weather']])
    decision = analyze_weather(temp, conditions)
    print(f"Received weather data for {data['name']}: {
          temp}°C, Conditions: {conditions}")
    print(decision)
    ch.basic_ack(delivery_tag=method.delivery_tag)


def analyze_weather(temp, conditions):
    if temp > 10 and temp < 30 and 'rain' not in conditions.lower():
        return "It's a good day for a walk!"
    else:
        return "Not a great day for a walk."


def start_weather_consumer():
    start_consumer('weather_data', process_weather_data)


if __name__ == '__main__':
    start_weather_consumer()
