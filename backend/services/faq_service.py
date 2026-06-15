from backend.database.mysql_connection import db

class FaqService:
    def get_answer(self, query):
        conn = db.connect()
        if not conn:
            return None
            
        cursor = conn.cursor(dictionary=True)
        # Fetch all FAQs to do fuzzy matching since speech recognition might have slight variations
        cursor.execute("SELECT id, question, answer FROM faq_data")
        faqs = cursor.fetchall()
        cursor.close()
        
        best_match = None
        highest_score = 0
        
        for faq in faqs:
            # We can use simple substring match or fuzzy matching.
            # For simplicity, we just check if key words exist or use basic similarity
            # Here we just do a basic fallback string inclusion check
            if query.lower() in faq['question'].lower() or faq['question'].lower() in query.lower():
                highest_score = 100
                best_match = faq
                break
                
        if best_match:
            # Increment frequency
            cursor = conn.cursor()
            cursor.execute("UPDATE faq_data SET frequency = frequency + 1 WHERE id = %s", (best_match['id'],))
            conn.commit()
            cursor.close()
            return best_match['answer']
            
        return None
