from backend.database.mysql_connection import db

class QueryLogRepository:
    """Repository for query_logs."""
    
    def log_query(self, query_text, intent, entity, keywords, match_score, response_text, is_successful, response_source):
        conn = db.connect()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO query_logs 
                (query_text, intent, entity, extracted_keywords, match_score, response_text, is_successful, response_source) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (query_text, intent, entity, keywords, float(match_score), response_text, is_successful, response_source))
            conn.commit()
        except Exception as e:
            print(f"Logging error: {e}")
            conn.rollback()
        finally:
            cursor.close()

    def get_recent_queries(self, limit=10):
        """Fetch the most recent successful queries."""
        conn = db.connect()
        if not conn:
            return []
            
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT query_text, response_text, response_source 
                FROM query_logs 
                WHERE is_successful = 1 
                ORDER BY timestamp DESC 
                LIMIT %s
            """, (limit,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Fetch recent queries error: {e}")
            return []
        finally:
            cursor.close()
