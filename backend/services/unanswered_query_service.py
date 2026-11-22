from backend.database.mysql_connection import db

class UnansweredQueryService:
    def record_query(self, query):
        conn = db.connect()
        if not conn:
            return
            
        cursor = conn.cursor()
        
        # Check if query already exists
        cursor.execute("SELECT id, frequency FROM unanswered_queries WHERE query_text = %s", (query,))
        result = cursor.fetchone()

        if result:
            # Query exists, increment frequency
            cursor.execute("UPDATE unanswered_queries SET frequency = frequency + 1 WHERE id = %s", (result[0],))
        else:
            # New unanswered query
            cursor.execute("INSERT INTO unanswered_queries (query_text) VALUES (%s)", (query,))
            
        conn.commit()
        cursor.close()
        conn.close()
