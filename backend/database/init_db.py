import os
import bcrypt
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()

def init_db():
    try:
        # First connect without database to create it if it doesn't exist
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "127.0.0.1"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASS", "")
        )
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {os.getenv('DB_NAME', 'gramai_db')}")
            print("Database created or already exists.")
            cursor.close()
            connection.close()

        # Connect to the database and run schema.sql
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "127.0.0.1"),
            database=os.getenv("DB_NAME", "gramai_db"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASS", "")
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
            
            # Seed Admin User
            cursor.execute("SELECT id FROM admin_users WHERE username = 'admin'")
            if not cursor.fetchone():
                password = b"Abhinash@19"
                hashed = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')
                cursor.execute("""
                    INSERT INTO admin_users (username, password_hash, full_name, designation, office_name, role)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, ('admin', hashed, 'Authorized Official', 'Sachivalayam Secretary', 'Village Secretariat', 'Village Admin'))
                print("Seeded initial admin account.")

            # Seed FAQ
            cursor.execute("SELECT id FROM faq_data")
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO faq_data (question, answer) VALUES
                    ('How do I apply for the old-age pension?', 'Aadhaar card, income certificate, and age proof are required for the old-age pension.'),
                    ('What documents are needed for a new ration card?', 'You need address proof, identity proof, and a passport-size photograph.'),
                    ('When will the next farmer subsidy be released?', 'The next farmer subsidy (Rythu Bandhu) is scheduled to be released next month.')
                """)
                print("Seeded initial FAQ data.")

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
