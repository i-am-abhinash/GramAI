import mysql.connector

def run_migrations():
    conn = mysql.connector.connect(
        host='127.0.0.1',
        database='gramai_db',
        user='root',
        password='Abhinash@19'
    )
    cursor = conn.cursor()

    migrations = [
        """
        CREATE TABLE IF NOT EXISTS feedback (
            id INT AUTO_INCREMENT PRIMARY KEY,
            query_text VARCHAR(255) NOT NULL,
            response_text TEXT,
            is_helpful BOOLEAN NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS cached_responses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            query_text VARCHAR(255) NOT NULL UNIQUE,
            response_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS query_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            query_text TEXT NOT NULL,
            intent VARCHAR(100),
            entity VARCHAR(100),
            extracted_keywords TEXT,
            match_score FLOAT,
            response_text TEXT,
            is_successful BOOLEAN,
            response_source VARCHAR(255),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    ]

    # Alter government_schemes
    try:
        cursor.execute("ALTER TABLE government_schemes ADD COLUMN category VARCHAR(100) AFTER name")
    except Exception as e:
        pass # Already exists
    
    try:
        cursor.execute("ALTER TABLE government_schemes ADD COLUMN benefits TEXT AFTER required_documents")
    except Exception as e:
        pass

    try:
        cursor.execute("ALTER TABLE government_schemes ADD COLUMN application_process TEXT AFTER benefits")
    except Exception as e:
        pass

    try:
        cursor.execute("ALTER TABLE government_schemes ADD COLUMN source_name VARCHAR(255) AFTER application_process")
    except Exception as e:
        pass

    try:
        cursor.execute("ALTER TABLE government_schemes ADD COLUMN source_url VARCHAR(255) AFTER source_name")
    except Exception as e:
        pass

    try:
        cursor.execute("ALTER TABLE government_schemes ADD COLUMN last_updated_date DATE AFTER source_url")
    except Exception as e:
        pass

    # Alter unanswered_queries
    try:
        cursor.execute("ALTER TABLE unanswered_queries ADD COLUMN status VARCHAR(50) DEFAULT 'Pending' AFTER frequency")
    except Exception as e:
        pass

    try:
        cursor.execute("ALTER TABLE unanswered_queries ADD COLUMN first_asked_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP AFTER status")
    except Exception as e:
        pass

    for query in migrations:
        try:
            cursor.execute(query)
        except Exception as e:
            print(f"Error executing {query}: {e}")

    conn.commit()
    cursor.close()
    conn.close()
    print("Database migrations applied successfully!")

if __name__ == '__main__':
    run_migrations()
