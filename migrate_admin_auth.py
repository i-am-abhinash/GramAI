import mysql.connector
import bcrypt

def run_admin_auth_migrations():
    conn = mysql.connector.connect(
        host='127.0.0.1',
        database='gramai_db',
        user='root',
        password='Abhinash@19'
    )
    cursor = conn.cursor()

    try:
        # Create admin_users table
        cursor.execute("DROP TABLE IF EXISTS admin_users")
        cursor.execute("""
            CREATE TABLE admin_users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                full_name VARCHAR(100) NOT NULL,
                designation VARCHAR(100),
                office_name VARCHAR(100),
                role ENUM('Village Admin', 'Mandal Admin', 'District Admin', 'Super Admin') DEFAULT 'Village Admin',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Create user_feedback table for tracking response ratings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_feedback (
                id INT AUTO_INCREMENT PRIMARY KEY,
                query_text TEXT,
                response_text TEXT,
                is_helpful BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("Ensured user_feedback table exists.")
        
        # Check if seed user exists
        cursor.execute("SELECT id FROM admin_users WHERE username = 'admin'")
        if not cursor.fetchone():
            # Seed the initial Village Admin account
            password = b"Abhinash@19"
            hashed = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')
            
            cursor.execute("""
                INSERT INTO admin_users (username, password_hash, full_name, designation, office_name, role)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, ('admin', hashed, 'Authorized Official', 'Sachivalayam Secretary', 'Village Secretariat', 'Village Admin'))
            print("Seeded initial Village Admin account (admin / Abhinash@19).")
        
        conn.commit()
        print("Admin Auth Migrations complete!")
    except Exception as e:
        print(f"Migration error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    run_admin_auth_migrations()
