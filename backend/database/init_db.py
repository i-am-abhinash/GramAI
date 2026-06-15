import mysql.connector
from mysql.connector import Error
import os

def init_db():
    try:
        # First connect without database to create it if it doesn't exist
        connection = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='Abhinash@19'
        )
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS gramai_db")
            print("Database created or already exists.")
            cursor.close()
            connection.close()

        # Connect to the database and run schema.sql
        connection = mysql.connector.connect(
            host='127.0.0.1',
            database='gramai_db',
            user='root',
            password='Abhinash@19'
        )
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Read schema.sql
            schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
            with open(schema_path, 'r', encoding='utf-8') as f:
                sql_file = f.read()
            
            # Execute multiple statements
            sql_commands = sql_file.split(';')
            for command in sql_commands:
                try:
                    if command.strip() != '':
                        cursor.execute(command)
                except Error as e:
                    print(f"Command skipped/failed: {e}")
            
            connection.commit()
            print("Database schema initialized successfully.")
            
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

if __name__ == '__main__':
    init_db()
