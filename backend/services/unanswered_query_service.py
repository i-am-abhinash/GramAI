from backend.database.mysql_connection import db

class UnansweredQueryService:
    def record_query(self, query):
        conn = db.connect()
        if not conn:
            return
            
        cursor = conn.cursor()
        
        # Check if query already exists
        cursor.execute("SELECT id, frequency FROM unanswered_queries WHERE raw_query_telugu = %s", (query,))
        result = cursor.fetchone()
        
        if result:
            # Increment frequency
            cursor.execute("UPDATE unanswered_queries SET frequency = frequency + 1 WHERE id = %s", (result[0],))
        else:
            # Insert new
            cursor.execute("INSERT INTO unanswered_queries (raw_query_telugu) VALUES (%s)", (query,))
            
        conn.commit()
        cursor.close()
