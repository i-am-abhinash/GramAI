import mysql.connector

def clear_all_tables():
    print("Connecting to the database...")
    try:
        conn = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='Abhinash@19',
            database='gramai_db'
        )
        cursor = conn.cursor()
        
        print("Clearing all data...")
        # Ignore foreign key constraints temporarily if any exist
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        
        # Truncate tables to wipe them completely
        cursor.execute("TRUNCATE TABLE query_logs;")
        cursor.execute("TRUNCATE TABLE unanswered_queries;")
        cursor.execute("TRUNCATE TABLE faq_data;")
        cursor.execute("TRUNCATE TABLE government_schemes;")
        
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        conn.commit()
        
        print("Successfully wiped all data! The database is now completely empty.")
        
    except mysql.connector.Error as e:
        print(f"Error: {e}")
        print("Make sure the GramAI app is closed before running this script, as it may lock the tables.")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    clear_all_tables()
