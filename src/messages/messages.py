import json
import os
import pika
from dotenv import load_dotenv

load_dotenv()


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
    print(f" [x] Sent {message} to {queue_name}")
    connection.close()


def start_consumer(queue_name, callback):
    connection = create_connection()
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name, on_message_callback=callback)
    print(f' [*] Waiting for messages in {queue_name}. To exit press CTRL+C')
    channel.start_consuming()
