import mysql.connector

def run_sync_migrations():
    conn = mysql.connector.connect(
        host='127.0.0.1',
        database='gramai_db',
        user='root',
        password='Abhinash@19'
    )
    cursor = conn.cursor()

    migrations = [
        """
        CREATE TABLE IF NOT EXISTS imported_schemes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            category VARCHAR(100),
            description TEXT,
            eligibility TEXT,
            required_documents TEXT,
            benefits TEXT,
            application_process TEXT,
            keywords TEXT,
            source_name VARCHAR(255),
            source_url VARCHAR(255),
            last_verified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_sync_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS sync_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            sync_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            records_imported INT DEFAULT 0,
            records_updated INT DEFAULT 0,
            failed_imports INT DEFAULT 0,
            status VARCHAR(50)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS pending_reviews (
            id INT AUTO_INCREMENT PRIMARY KEY,
            imported_scheme_id INT,
            issue_reason VARCHAR(255),
            status VARCHAR(50) DEFAULT 'Pending Review',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS change_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            imported_scheme_id INT,
            change_description TEXT,
            changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    ]

    for q in migrations:
        try:
            cursor.execute(q)
        except Exception as e:
            print(f"Error creating tables: {e}")

    # Migrate data from government_schemes to imported_schemes
    try:
        cursor.execute("SELECT name, category, description, eligibility, required_documents, benefits, application_process, keywords, source_name, source_url FROM government_schemes")
        schemes = cursor.fetchall()
        
        insert_q = """
            INSERT INTO imported_schemes 
            (name, category, description, eligibility, required_documents, benefits, application_process, keywords, source_name, source_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        for s in schemes:
            # Check if exists to prevent duplicate migration runs
            cursor.execute("SELECT id FROM imported_schemes WHERE name=%s", (s[0],))
            if not cursor.fetchone():
                cursor.execute(insert_q, s)
                
        print("Migrated schemes data.")
    except Exception as e:
        print(f"Migration error (table might not exist or already dropped): {e}")

    conn.commit()
    cursor.close()
    conn.close()
    print("Automated Sync Migrations complete!")

if __name__ == '__main__':
    run_sync_migrations()
