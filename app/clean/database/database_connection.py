import os

import mysql.connector


class Database_connection:
    def __init__(self):
        pass

    def connection(self):
        return mysql.connector.connect(
            host=os.getenv("MYSQL_HOST", "mysql"),
            user=os.getenv("MYSQL_USER", "crypto"),
            password=os.environ["MYSQL_PASSWORD"],
            connection_timeout=10,
            database=os.getenv("MYSQL_DATABASE", "crypto"),
            port=int(os.getenv("MYSQL_PORT", "3306")),
        )
