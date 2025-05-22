import mysql.connector
from dotenv import load_dotenv
class Database_connection:
    def __init__(self):
        pass

    def connection(self):
        load_dotenv()
        mydb = mysql.connector.connect(
            host="mysql",#Docker
            #host="localhost",#Localhost
            user="epitech",
            password="epitech",
            database="crypto",
            port=3306
        )
        return mydb
