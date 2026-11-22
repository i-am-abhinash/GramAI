import os
import mysql.connector
from mysql.connector import pooling
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class DatabaseConnection:
    _pool = None
    
    def __new__(cls):
        if cls._pool is None:
            cls._pool = super(DatabaseConnection, cls).__new__(cls)
            try:
                cls._pool.pool = mysql.connector.pooling.MySQLConnectionPool(
                    pool_name="gramai_pool",
                    pool_size=5,
                    pool_reset_session=True,
                    host=os.getenv("DB_HOST", "127.0.0.1"),
                    database=os.getenv("DB_NAME", "gramai_db"),
                    user=os.getenv("DB_USER", "root"),
                    password=os.getenv("DB_PASS", ""),
                    autocommit=True
                )
            except Error as e:
                print(f"Error initializing connection pool: {e}")
                cls._pool.pool = None
        return cls._pool

    def connect(self):
        try:
            if self.pool:
                return self.pool.get_connection()
            return None
        except Error as e:
            print(f"Error getting connection from pool: {e}")
            return None

# Singleton instance for easy access
db = DatabaseConnection()
