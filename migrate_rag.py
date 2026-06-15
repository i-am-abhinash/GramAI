import mysql.connector

def run_rag_migrations():
    conn = mysql.connector.connect(
        host='127.0.0.1',
        database='gramai_db',
        user='root',
        password='Abhinash@19'
    )
    cursor = conn.cursor()

    try:
        # Check if entity column exists
        cursor.execute("SHOW COLUMNS FROM query_logs LIKE 'entity'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE query_logs ADD COLUMN entity VARCHAR(255)")
            print("Added 'entity' column to query_logs.")
        
        # Check if response_source column exists
        cursor.execute("SHOW COLUMNS FROM query_logs LIKE 'response_source'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE query_logs ADD COLUMN response_source VARCHAR(100)")
            print("Added 'response_source' column to query_logs.")

        conn.commit()
        print("RAG Migrations complete!")
    except Exception as e:
        print(f"Migration error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    run_rag_migrations()
