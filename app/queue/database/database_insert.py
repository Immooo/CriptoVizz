import json
import os
import pika
from .database_connection import Database_connection

class Database_insert:
    def __init__(self):
        self.db_connection = Database_connection()

    def insert_seeder_into_db(self, message):
        try:
            db = self.db_connection.connection()
            cursor = db.cursor()
            with open('database/crypto_seeder_hourly_last_15_days.sql', 'r') as sql_file:
                result_iterator = cursor.execute(sql_file.read(), multi=True)
                for res in result_iterator:
                    print("Inserting seeder data into database: ", res)
                db.commit()
        except Exception as e:
            print("Error inserting into database:", e)
        finally:
            cursor.close()
            db.close()

    def insert_into_db(self, message):
        try:
            print("Inserting into database:", message)
            db = self.db_connection.connection()
            cursor = db.cursor()

            columns = ', '.join(str(x).replace('/', '_') for x in message.keys())
            values = ', '.join("'" + str(x).replace('/', '_') + "'" for x in message.values())
            sql = "INSERT INTO crypto ( %s ) VALUES ( %s );" % (columns, values)

            cursor.execute(sql)
            db.commit()
        except Exception as e:
            print("Error inserting into database:", e)
        finally:
            cursor.close()
            db.close()

    def consume_queue(self):
        try:
            url = os.environ.get('CLOUDAMQP_URL', 'amqp://guest:guest@rabbitmq:5672')
            params = pika.URLParameters(url)

            with pika.BlockingConnection(params) as connection:
                channel = connection.channel()

                # Assurez-vous que la file 'crypto_queue' existe
                channel.queue_declare(queue='crypto_queue', durable=True)

                def callback(ch, method, properties, body):
                    print("Received message:", body)
                    message = json.loads(body)
                    self.insert_into_db(message)
                    print("Message processed:", body)

                # Configurez le consommateur
                channel.basic_consume(queue='crypto_queue', on_message_callback=callback, auto_ack=True)

                print("Before start_consuming")
                # Commencez à consommer (bloquant)
                channel.start_consuming()
                print("After start_consuming")

        except pika.exceptions.AMQPError as amqp_error:
            print("AMQP Error:", amqp_error)
            # Gérer l'erreur AMQP (par exemple, journaliser l'erreur, dormir, ou prendre des mesures appropriées)
        except Exception as e:
            print("Error consuming queue:", e)
