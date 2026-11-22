from backend.database.mysql_connection import db

class UnansweredQueryRepository:
    """Repository for unanswered_queries."""
    
    def record_query(self, query_text, intent, entity):
        conn = db.connect()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            # Check if query already exists
            cursor.execute("SELECT id, frequency FROM unanswered_queries WHERE query_text = %s", (query_text,))
            existing = cursor.fetchone()
            
            if existing:
                query_id, current_freq = existing
                cursor.execute("""
                    UPDATE unanswered_queries 
                    SET frequency = %s, last_asked = CURRENT_TIMESTAMP 
                    WHERE id = %s
                """, (current_freq + 1, query_id))
            else:
                cursor.execute("""
                    INSERT INTO unanswered_queries (query_text, frequency, status) 
                    VALUES (%s, 1, 'Pending')
                """, (query_text,))
            conn.commit()
        except Exception as e:
            print(f"Error recording unanswered query: {e}")
            conn.rollback()
        finally:
            if 'cursor' in locals() and cursor: cursor.close()
            if conn: conn.close()
