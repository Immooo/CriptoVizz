import os
import time
import json
import pika
from cryptoscrap import Cryptoscrap

class RabbitMQPublisher:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.url = os.environ.get('CLOUDAMQP_URL', 'amqp://guest:guest@rabbitmq:5672')
        self.params = pika.URLParameters(self.url)
        self.connect()
    
    def connect(self):
        """Establish connection to RabbitMQ"""
        max_retries = 5
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                print(f"🔄 Tentative connexion RabbitMQ #{retry_count + 1}")
                self.connection = pika.BlockingConnection(self.params)
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue='crypto_queue', durable=True)
                print("✅ Connexion RabbitMQ établie")
                return True
            except pika.exceptions.AMQPConnectionError as e:
                retry_count += 1
                print(f"❌ Erreur de connexion à RabbitMQ (tentative {retry_count}/{max_retries}): {e}")
                if retry_count < max_retries:
                    time.sleep(5)  # Wait 5 seconds before retry
                else:
                    print("❌ Impossible de se connecter à RabbitMQ après plusieurs tentatives")
                    return False
    
    def send_message(self, data):
        """Send message to RabbitMQ"""
        try:
            # Check if connection is still alive
            if not self.connection or self.connection.is_closed:
                print("🔄 Reconnexion à RabbitMQ nécessaire")
                if not self.connect():
                    return False
            
            self.channel.basic_publish(
                exchange='',
                routing_key='crypto_queue',
                body=json.dumps(data),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make the message persistent
                )
            )
            print("✅ Message envoyé avec succès à RabbitMQ")
            print(f"📋 {data}")
            return True
            
        except (pika.exceptions.AMQPConnectionError, pika.exceptions.AMQPChannelError) as e:
            print(f"❌ Erreur lors de l'envoi du message: {e}")
            # Try to reconnect
            if self.connect():
                # Retry sending the message
                try:
                    self.channel.basic_publish(
                        exchange='',
                        routing_key='crypto_queue',
                        body=json.dumps(data),
                        properties=pika.BasicProperties(
                            delivery_mode=2,
                        )
                    )
                    print("✅ Message envoyé après reconnexion")
                    return True
                except Exception as e:
                    print(f"❌ Échec de l'envoi après reconnexion: {e}")
                    return False
            return False
    
    def close(self):
        """Close RabbitMQ connection"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()

if __name__ == "__main__":
    starttime = time.monotonic()
    publisher = RabbitMQPublisher()
    cryptoscrap_instance = Cryptoscrap()
    
    try:
        while True:
            # Effectuer le scraping
            scraped_data = cryptoscrap_instance.cryptoscrapfct()
            
            # Envoyer les données à RabbitMQ
            if scraped_data:
                for data_point in scraped_data:
                    publisher.send_message(data_point)
            else:
                print("⚠️ Aucune donnée récupérée lors du scraping")
            
            # Wait for next minute
            time.sleep(60.0 - ((time.monotonic() - starttime) % 60.0))
            
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du scraper")
        publisher.close()
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        publisher.close()