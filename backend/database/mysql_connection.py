import mysql.connector
from mysql.connector import Error

class DatabaseConnection:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance.connection = None
        return cls._instance

    def connect(self):
        try:
            connection = mysql.connector.connect(
                host='127.0.0.1',
                database='gramai_db',
                user='root',
                password='Abhinash@19',
                autocommit=True
            )
            return connection
        except Error as e:
            print(f"Error while connecting to MySQL: {e}")
            return None

# Singleton instance for easy access
db = DatabaseConnection()
