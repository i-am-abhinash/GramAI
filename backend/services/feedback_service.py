from backend.database.mysql_connection import db

class FeedbackService:
    def record_feedback(self, query_text, response_text, is_helpful):
        conn = db.connect()
        if not conn:
            return
            
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO feedback (query_text, response_text, is_helpful) VALUES (%s, %s, %s)",
            (query_text, response_text, is_helpful)
        )
        conn.commit()
        cursor.close()
        conn.close()
