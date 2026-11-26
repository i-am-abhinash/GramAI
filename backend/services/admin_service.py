from backend.database.mysql_connection import db

class AdminService:
    def get_imported_schemes(self):
        conn = db.connect()
        if not conn:
            return []
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, category, description, eligibility, required_documents, benefits, application_process, source_name, source_url, last_verified_date, last_sync_date FROM imported_schemes ORDER BY last_sync_date DESC")
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results

    def trigger_sync(self):
        from backend.services.sync_service import GovernmentSchemeSyncService
        sync = GovernmentSchemeSyncService()
        return sync.run_sync()

    def get_pending_reviews(self):
        conn = db.connect()
        if not conn:
            return []
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT pr.id as review_id, pr.issue_reason, pr.status, pr.created_at,
                   s.id as scheme_id, s.name, s.description, s.eligibility, s.source_url
            FROM pending_reviews pr
            JOIN imported_schemes s ON pr.imported_scheme_id = s.id
            WHERE pr.status = 'Pending Review'
            ORDER BY pr.created_at DESC
        """)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results

    def update_review_status(self, review_id, scheme_id, action, corrected_eligibility=None, user_id=None):
        # Legacy records are not a publication surface. Keep the original data
        # until the full evidence-based editor is implemented.
        if action != "Reject":
            return False
        conn = db.connect()
        if not conn:
            return False
        cursor = None
        try:
            conn.autocommit = False
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE pending_reviews SET status='Rejected', resolved_by=%s, resolved_at=NOW() "
                "WHERE id=%s AND imported_scheme_id=%s AND status='Pending Review'",
                (user_id, review_id, scheme_id),
            )
            changed = cursor.rowcount == 1
            if changed:
                cursor.execute("UPDATE scheme_imports SET status='rejected' WHERE legacy_scheme_id=%s", (scheme_id,))
            conn.commit()
            return changed
        except Exception as exc:
            conn.rollback()
            print(f"Legacy review not changed: {exc}")
            return False
        finally:
            if cursor is not None:
                cursor.close()
            conn.close()

    def get_sync_logs(self, limit=50):
        conn = db.connect()
        if not conn:
            return []
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM sync_logs ORDER BY sync_time DESC LIMIT %s", (limit,))
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results

    def get_dashboard_stats(self):
        conn = db.connect()
        if not conn:
            return {}
        cursor = conn.cursor(dictionary=True)
        stats = {}
        
        # Total Questions (from query_logs + unanswered_queries if not in query_logs, but let's say query_logs has all)
        cursor.execute("SELECT COUNT(*) as c FROM query_logs")
        stats['total_questions'] = cursor.fetchone()['c']
        
        # Answered Questions
        cursor.execute("SELECT COUNT(*) as c FROM query_logs WHERE is_successful = 1")
        stats['answered_questions'] = cursor.fetchone()['c']
        
        # Unanswered Questions
        cursor.execute("SELECT COUNT(*) as c FROM unanswered_queries")
        stats['unanswered_questions'] = cursor.fetchone()['c']
        
        # Flagged Responses (assuming we track this in user_feedback with is_helpful = 0)
        cursor.execute("SELECT COUNT(*) as c FROM user_feedback WHERE is_helpful = 0")
        stats['flagged_responses'] = cursor.fetchone()['c']
        
        cursor.close()
        conn.close()
        return stats

    def get_unanswered_queries(self):
        conn = db.connect()
        if not conn:
            return []
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, query_text, frequency, last_asked, status, first_asked_date FROM unanswered_queries ORDER BY last_asked DESC")
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results

    def update_unanswered_query_status(self, query_id, status):
        conn = db.connect()
        if conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE unanswered_queries SET status = %s WHERE id = %s", (status, query_id))
            conn.commit()
            cursor.close()
            conn.close()

    def publish_cached_response(self, query_text, response_text):
        conn = db.connect()
        if conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO cached_responses (query_text, response_text) VALUES (%s, %s) ON DUPLICATE KEY UPDATE response_text=%s", (query_text, response_text, response_text))
            conn.commit()
            cursor.close()
            conn.close()

    def get_all_faqs(self):
        conn = db.connect()
        if not conn:
            return []
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, question, answer, frequency FROM faq_data ORDER BY frequency DESC")
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results

    def add_faq(self, question, answer):
        conn = db.connect()
        if conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO faq_data (question, answer, frequency) VALUES (%s, %s, 0)", (question, answer))
            conn.commit()
            cursor.close()
            conn.close()

    def update_faq(self, faq_id, question, answer):
        conn = db.connect()
        if conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE faq_data SET question = %s, answer = %s WHERE id = %s", (question, answer, faq_id))
            conn.commit()
            cursor.close()
            conn.close()

    def delete_faq(self, faq_id):
        conn = db.connect()
        if conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM faq_data WHERE id = %s", (faq_id,))
            conn.commit()
            cursor.close()
            conn.close()

    def get_query_logs(self, limit=100):
        conn = db.connect()
        if not conn:
            return []
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, query_text, response_text, is_successful, timestamp as created_at FROM query_logs ORDER BY timestamp DESC LIMIT %s", (limit,))
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
