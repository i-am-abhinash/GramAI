from backend.database.mysql_connection import db

class SchemeRepository:
    """Repository pattern for imported schemes."""
    
    def get_schemes_by_category(self, category):
        """Fetch schemes filtered by category (entity)."""
        conn = db.connect()
        if not conn:
            return []
        
        cursor = conn.cursor(dictionary=True)
        # Using LIKE to do partial matching or exact if preferred
        # Since category in DB might be 'Pension' and entity 'pension'
        cursor.execute("""
            SELECT id, name, category, description, eligibility, required_documents, 
                   benefits, application_process, keywords, source_url
            FROM imported_schemes
            WHERE LOWER(category) = %s OR category = 'Welfare' OR category = 'Other'
        """, (category.lower(),))
        
        results = cursor.fetchall()
        cursor.close()
        return results

    def get_all_schemes(self):
        """Fallback to all schemes if entity is not detected."""
        conn = db.connect()
        if not conn:
            return []
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, name, category, description, eligibility, required_documents, 
                   benefits, application_process, keywords, source_url
            FROM imported_schemes
        """)
        
        results = cursor.fetchall()
        cursor.close()
        return results
