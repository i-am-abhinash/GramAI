"""Create or reset a GramAI administrator account in the configured MySQL database.

Run locally: python setup_admin.py
Passwords are entered privately and stored only as bcrypt hashes.
"""
from getpass import getpass
import bcrypt
from backend.database.mysql_connection import db


def main():
    print("GramAI — Administrator Account Setup")
    username = input("Admin username: ").strip()
    if not username or len(username) > 80:
        raise SystemExit("Username must contain 1–80 characters.")
    full_name = input("Full name [GramAI Administrator]: ").strip() or "GramAI Administrator"
    designation = input("Designation [Administrator]: ").strip() or "Administrator"
    office_name = input("Office name [GramAI]: ").strip() or "GramAI"

    password = getpass("New admin password (12+ characters): ")
    confirmation = getpass("Confirm admin password: ")
    if len(password) < 12:
        raise SystemExit("Use a password of at least 12 characters.")
    if password != confirmation:
        raise SystemExit("Passwords did not match.")
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    conn = db.connect()
    if conn is None:
        raise SystemExit("Cannot connect to MySQL. Check backend/database/mysql_connection.py.")
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM admin_users WHERE username = %s", (username,))
        existing = cursor.fetchone()
        if existing:
            confirm = input("Account exists. Reset its password and activate it? [y/N]: ").strip().lower()
            if confirm != "y":
                print("No changes made.")
                return
            cursor.execute(
                """UPDATE admin_users SET password_hash=%s, full_name=%s,
                   designation=%s, office_name=%s, role=%s, is_active=%s WHERE username=%s""",
                (hashed, full_name, designation, office_name, "admin", 1, username),
            )
        else:
            cursor.execute(
                """INSERT INTO admin_users
                   (username, password_hash, full_name, designation, office_name, role, is_active)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (username, hashed, full_name, designation, office_name, "admin", 1),
            )
        conn.commit()
        print(f"Administrator '{username}' is ready. You can now log in to GramAI.")
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
