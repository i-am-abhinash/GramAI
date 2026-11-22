import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
from backend.database.init_db import init_db

load_dotenv()

def reset_database():
    try:
        print("WARNING: This will drop the database and recreate it from scratch.")
        print("All data will be lost.")
        
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "127.0.0.1"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASS", "")
        )
        if connection.is_connected():
            cursor = connection.cursor()
            db_name = os.getenv('DB_NAME', 'gramai_db')
            
            print(f"Dropping database {db_name}...")
            cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
            
            print(f"Recreating database {db_name}...")
            cursor.execute(f"CREATE DATABASE {db_name}")
            
            cursor.close()
            connection.close()
            
            print("Database dropped and recreated. Initializing schema and seed data...")
            init_db()
            
    except Error as e:
        print(f"Error while resetting database: {e}")

if __name__ == '__main__':
    reset_database()
