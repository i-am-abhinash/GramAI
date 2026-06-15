class RAGService:
    """Builds context and generates AI response based strictly on retrieved scheme data."""
    
    def generate_response(self, intent, scheme_data):
        """
        Mock LLM Generation Template.
        Simulates: 'Answer the user's question using ONLY the provided government scheme information.'
        """
        if not scheme_data:
            return "ఈ సమాచారం ప్రస్తుతం మా నాలెడ్జ్ బేస్‌లో లేదు." # Info not available
            
        scheme_name = scheme_data.get('name', 'ఈ పథకం')
        
        # 1. Context Builder: Extract only what is needed based on Intent
        context = ""
        
        if intent == "eligibility":
            context = scheme_data.get('eligibility', '')
            prefix = f"{scheme_name} కు అర్హతలు: " # Qualifications for...
        elif intent == "required_documents":
            context = scheme_data.get('required_documents', '')
            prefix = f"{scheme_name} కు కావాల్సిన పత్రాలు: " # Required docs for...
        elif intent == "benefits":
            context = scheme_data.get('benefits', '')
            prefix = f"{scheme_name} ద్వారా వచ్చే లాభాలు: " # Benefits of...
        elif intent == "application_process":
            context = scheme_data.get('application_process', '')
            prefix = f"{scheme_name} కు ఎలా దరఖాస్తు చేయాలి: " # How to apply for...
        else:
            # Default: scheme_information or scheme_search
            context = scheme_data.get('description', '')
            prefix = f"{scheme_name} వివరాలు: "
            
        # 2. AI Synthesis Constraint Check
        if not context or context.strip() == "":
            return f"{scheme_name} కు సంబంధించిన ఈ నిర్దిష్ట సమాచారం ప్రస్తుతం అందుబాటులో లేదు."
            
        # 3. Final Output Generation
        return f"{prefix}{context}"
