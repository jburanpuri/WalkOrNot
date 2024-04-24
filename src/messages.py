import logging
import json
import os
import pika
from dotenv import load_dotenv
from database import Database
from weather_service import get_weather_data

load_dotenv()

db = Database()


def create_connection():
    url = os.getenv('CLOUDAMQP_URL')
    params = pika.URLParameters(url)
    return pika.BlockingConnection(params)


def send_to_queue(queue_name, message):
    connection = create_connection()
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        ))
    print(" [x] Sent %r to %r" % (message, queue_name))
    connection.close()


def start_consumer(queue_name, callback):
    connection = create_connection()
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name, on_message_callback=callback)
    print(' [*] Waiting for messages in %r. To exit press CTRL+C' % queue_name)
    channel.start_consuming()


logging.basicConfig(level=logging.DEBUG)


def process_weather_request(ch, method, properties, body):
    try:
        city = json.loads(body)['city']
        logging.debug("Received weather request for city: " + city)
        weather_data = get_weather_data(city)
        if weather_data:
            logging.debug("Weather data fetched: " + str(weather_data))
            db.save_request_to_db(city, weather_data['main']['temp'])
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            logging.error("Failed to fetch weather data for city: " + city)
    except Exception as e:
        logging.error("An error occurred: " + str(e))
