import json
import os
import pika
import time
import mysql.connector.pooling
from .database_connection import Database_connection

class Database_insert:
    def __init__(self):
        self.reconnect_delay = 5
        self.connection_pool = None
        self.init_connection_pool()

    def init_connection_pool(self):
        """Initialize MySQL connection pool"""
        try:
            print("🔧 Initialisation du pool de connexions MySQL...")
            self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="crypto_pool",
                pool_size=5,  # Number of connections in the pool
                pool_reset_session=True,
                host="mysql",
                user="epitech",
                password="epitech",
                database="crypto",
                port=3306
            )
            print("✅ Pool de connexions MySQL créé avec succès")
        except Exception as e:
            print(f"❌ Erreur lors de la création du pool: {e}")
            # Fallback to regular connection
            self.db_connection = Database_connection()

    def get_connection(self):
        """Get a connection from the pool"""
        try:
            if self.connection_pool:
                return self.connection_pool.get_connection()
            else:
                # Fallback to regular connection
                return self.db_connection.connection()
        except Exception as e:
            print(f"⚠️ Erreur lors de l'obtention de la connexion: {e}")
            # Try to reinitialize the pool
            self.init_connection_pool()
            if self.connection_pool:
                return self.connection_pool.get_connection()
            else:
                return self.db_connection.connection()

    def insert_seeder_into_db(self, message):
        """Insert seeder data into database"""
        db = None
        cursor = None
        
        try:
            print("📝 Insertion des données du seeder...")
            db = self.get_connection()
            cursor = db.cursor()
            
            seeder_path = 'database/crypto_seeder_hourly_last_15_days.sql'
            if os.path.exists(seeder_path):
                with open(seeder_path, 'r') as sql_file:
                    sql_content = sql_file.read()
                    # Execute multi-statement SQL
                    for result in cursor.execute(sql_content, multi=True):
                        if result.with_rows:
                            print(f"Rows affected: {result.rowcount}")
                    db.commit()
                    print("✅ Données du seeder insérées avec succès")
            else:
                print(f"⚠️ Fichier seeder non trouvé: {seeder_path}")
                
        except Exception as e:
            print(f"❌ Error inserting seeder data: {e}")
            if db:
                db.rollback()
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()  # Returns connection to pool

    def validate_and_clean_data(self, data):
        """Validate and clean data before insertion"""
        # Ensure all required fields are present
        required_fields = ['cryptoName', 'cryptoPrice', 'cryptoDatetime', 
                          'cryptoClassement', 'cryptoVolume', 'cryptoChange']
        
        for field in required_fields:
            if field not in data:
                # Use default values for missing fields
                if field == 'cryptoVolume':
                    data[field] = '0'
                elif field == 'cryptoChange':
                    data[field] = '0'
                else:
                    raise ValueError(f"Missing required field: {field}")
        
        # Clean and validate data
        data['cryptoName'] = data['cryptoName'][:50]  # Truncate to 50 chars
        data['cryptoPrice'] = float(data['cryptoPrice'])
        data['cryptoClassement'] = int(data['cryptoClassement'])
        data['cryptoChange'] = float(data['cryptoChange'])
        
        return data

    def insert_into_db(self, message):
        """Insert crypto data into database"""
        db = None
        cursor = None
        
        try:
            # Validate and clean data
            message = self.validate_and_clean_data(message)
            
            # Get connection from pool
            db = self.get_connection()
            cursor = db.cursor()
            
            # Prepare SQL query
            sql = """INSERT INTO crypto 
                    (cryptoName, cryptoPrice, cryptoDatetime, cryptoClassement, cryptoVolume, cryptoChange) 
                    VALUES (%s, %s, %s, %s, %s, %s)"""
            
            values = (
                message['cryptoName'],
                message['cryptoPrice'],
                message['cryptoDatetime'],
                message['cryptoClassement'],
                message['cryptoVolume'],
                message['cryptoChange']
            )
            
            cursor.execute(sql, values)
            db.commit()
                        
        except Exception as e:
            print(f"❌ Error inserting into database: {e}")
            if db:
                db.rollback()
            raise  # Re-raise to trigger message requeue
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()  # Returns connection to pool

    def consume_queue(self):
        """Consume messages from RabbitMQ queue"""
        while True:
            try:
                url = os.environ.get('CLOUDAMQP_URL', 'amqp://guest:guest@rabbitmq:5672')
                params = pika.URLParameters(url)
                
                print("🔄 Connexion à RabbitMQ...")
                connection = pika.BlockingConnection(params)
                channel = connection.channel()
                
                # Declare queue (idempotent operation)
                channel.queue_declare(queue='crypto_queue', durable=True)
                
                # Set QoS - process up to 10 messages at a time
                channel.basic_qos(prefetch_count=10)
                
                def callback(ch, method, properties, body):
                    try:
                        message = json.loads(body)
                        self.insert_into_db(message)
                        
                        # Acknowledge message only after successful insert
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                        
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON decode error: {e}")
                        # Reject message and don't requeue
                        ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
                    except Exception as e:
                        print(f"❌ Error processing message: {e}")
                        # Requeue message for retry
                        ch.basic_reject(delivery_tag=method.delivery_tag, requeue=True)
                
                # Configure consumer with manual acknowledgment
                channel.basic_consume(
                    queue='crypto_queue', 
                    on_message_callback=callback, 
                    auto_ack=False
                )
                
                print("✅ Connecté à RabbitMQ. En attente de messages...")
                channel.start_consuming()
                
            except pika.exceptions.AMQPConnectionError as e:
                print(f"❌ RabbitMQ connection error: {e}")
                print(f"🔄 Reconnexion dans {self.reconnect_delay} secondes...")
                time.sleep(self.reconnect_delay)
            except KeyboardInterrupt:
                print("\n🛑 Arrêt du consommateur")
                if 'channel' in locals():
                    channel.stop_consuming()
                if 'connection' in locals():
                    connection.close()
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                time.sleep(self.reconnect_delay)