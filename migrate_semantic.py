import mysql.connector

def run_semantic_migrations():
    conn = mysql.connector.connect(
        host='127.0.0.1',
        database='gramai_db',
        user='root',
        password='Abhinash@19'
    )
    cursor = conn.cursor()

    # 1. Add keywords to government_schemes
    try:
        cursor.execute("ALTER TABLE government_schemes ADD COLUMN keywords TEXT AFTER benefits")
        print("Added keywords column to government_schemes")
    except Exception as e:
        print(f"Skipped adding keywords: {e}")

    # 2. Add semantic tracking columns to query_logs
    try:
        cursor.execute("ALTER TABLE query_logs ADD COLUMN intent VARCHAR(100) AFTER query_text")
        print("Added intent column to query_logs")
    except Exception as e:
        print(f"Skipped adding intent: {e}")

    try:
        cursor.execute("ALTER TABLE query_logs ADD COLUMN extracted_keywords TEXT AFTER intent")
        print("Added extracted_keywords column to query_logs")
    except Exception as e:
        print(f"Skipped adding extracted_keywords: {e}")

    try:
        cursor.execute("ALTER TABLE query_logs ADD COLUMN match_score FLOAT AFTER extracted_keywords")
        print("Added match_score column to query_logs")
    except Exception as e:
        print(f"Skipped adding match_score: {e}")

    # 3. Auto-populate existing schemes with some basic keywords
    cursor.execute("SELECT id, name, category, description FROM government_schemes WHERE keywords IS NULL OR keywords = ''")
    schemes = cursor.fetchall()
    
    for (s_id, name, category, description) in schemes:
        # Combine name and category as initial keywords
        cat = category if category else ""
        initial_keywords = f"{name} {cat}"
        # Add basic english equivalents if needed, but for now just use the telugu words
        cursor.execute("UPDATE government_schemes SET keywords = %s WHERE id = %s", (initial_keywords, s_id))

    conn.commit()
    cursor.close()
    conn.close()
    print("Semantic Migrations applied successfully!")

if __name__ == '__main__':
    run_semantic_migrations()
