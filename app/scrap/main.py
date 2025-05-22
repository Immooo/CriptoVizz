import os
import time
import json
import pika
from cryptoscrap import Cryptoscrap

def send_to_rabbitmq(data):
    url = os.environ.get('CLOUDAMQP_URL', 'amqp://guest:guest@rabbitmq:5672')
    params = pika.URLParameters(url)

    try:
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue='crypto_queue', durable=True)

        channel.basic_publish(exchange='',
                              routing_key='crypto_queue',
                              body=json.dumps(data),
                              properties=pika.BasicProperties(
                                  delivery_mode=2,  # Make the message persistent
                              ))

        connection.close()
    except pika.exceptions.AMQPConnectionError as e:
        print(f"Erreur de connexion à RabbitMQ : {e}")

if __name__ == "__main__":
    starttime = time.monotonic()

    while True:
        # Effectuer le scraping
        cryptoscrap_instance = Cryptoscrap()
        scraped_data = cryptoscrap_instance.cryptoscrapfct()

        # Envoyer les données à RabbitMQ
        if scraped_data:
            for data_point in scraped_data:
                send_to_rabbitmq(data_point)
                print(data_point)

        time.sleep(60.0 - ((time.monotonic() - starttime) % 60.0))
