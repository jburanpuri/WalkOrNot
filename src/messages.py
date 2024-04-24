import pika
import os
import json
from dotenv import load_dotenv

load_dotenv()


def setup_queue():
    connection = pika.BlockingConnection(
        pika.URLParameters(os.getenv('CLOUDAMQP_URL')))
    channel = connection.channel()
    channel.queue_declare(queue='walk_analysis', durable=True)
    return connection, channel


def send_message(message):
    connection, channel = setup_queue()
    channel.basic_publish(
        exchange='',
        routing_key='walk_analysis',
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        )
    )
    print("Message sent to queue")
    connection.close()
