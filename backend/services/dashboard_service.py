from backend.database.mysql_connection import db

class DashboardService:
    def get_top_faqs(self, limit=3):
        conn = db.connect()
        if not conn:
            return []
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT query_text as question FROM query_logs GROUP BY query_text ORDER BY MAX(created_at) DESC LIMIT %s", (limit,))
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return [row['question'] for row in results]

    def get_dashboard_stats(self):
        conn = db.connect()
        if not conn:
            return {"total": 0, "answered": 0, "unanswered": 0, "active": 1}
            
        cursor = conn.cursor()
        
        # Total queries
        cursor.execute("SELECT COUNT(*) FROM query_logs")
        total = cursor.fetchone()[0]
        
        # Answered queries
        cursor.execute("SELECT COUNT(*) FROM query_logs WHERE is_successful = True")
        answered = cursor.fetchone()[0]
        
        # Unanswered
        cursor.execute("SELECT COUNT(*) FROM unanswered_queries")
        unanswered = cursor.fetchone()[0]
        
        # Feedback count
        try:
            cursor.execute("SELECT COUNT(*) FROM feedback")
            feedback_count = cursor.fetchone()[0]
        except Exception:
            feedback_count = 0

        cursor.close()
        conn.close()
        
        return {
            "total": total,
            "answered": answered,
            "unanswered": unanswered,
            "active": 1, # Mock active kiosks
            "feedback": feedback_count
        }

    def get_most_asked(self, limit=5):
        conn = db.connect()
        if not conn:
            return []
            
        cursor = conn.cursor(dictionary=True)
        # Compute most asked directly from all recorded query_logs 
        # so that every asked question is counted and aggregated.
        query = """
            SELECT query_text as question, COUNT(*) as frequency 
            FROM query_logs 
            GROUP BY query_text 
            ORDER BY frequency DESC 
            LIMIT %s
        """
        cursor.execute(query, (limit,))
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return [(row['question'], row['frequency']) for row in results]
