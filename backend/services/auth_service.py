import bcrypt
from backend.database.mysql_connection import db

class AuthService:
    """Handles secure authentication for Government Administrators."""
    
    _current_user = None

    @classmethod
    def authenticate(cls, username, password):
        conn = db.connect()
        if not conn:
            return {"success": False, "message": "Database connection failed."}
            
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, username, password_hash, full_name, designation, office_name, role, is_active 
                FROM admin_users 
                WHERE username = %s
            """, (username,))
            
            user = cursor.fetchone()
            
            if not user:
                return {"success": False, "message": "Invalid username or password."}
                
            if not user['is_active']:
                return {"success": False, "message": "This account has been deactivated."}
                
            # Verify bcrypt password
            if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                session_user = {
                    "id": user['id'],
                    "username": user['username'],
                    "full_name": user['full_name'],
                    "designation": user['designation'],
                    "office_name": user['office_name'],
                    "role": user['role']
                }
                cls._current_user = session_user
                import time
                session_user['login_time'] = time.time()
                return {"success": True, "user": session_user}
            else:
                return {"success": False, "message": "Invalid username or password."}
                
        except Exception as e:
            return {"success": False, "message": f"Authentication error: {e}"}
        finally:
            if conn:
                cursor.close()
                conn.close()

    @classmethod
    def get_current_user(cls):
        return cls._current_user

    @classmethod
    def logout(cls):
        cls._current_user = None
