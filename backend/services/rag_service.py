class RAGService:
    """Grounded template responses using only scheme database fields."""
    def generate_response(self, intent, scheme_data, language="te"):
        en = str(language).lower().startswith("en")
        if not scheme_data:
            return "Information is currently unavailable." if en else "ఈ సమాచారం ప్రస్తుతం మా నాలెడ్జ్ బేస్‌లో లేదు."
        name = scheme_data.get("name", "this scheme" if en else "ఈ పథకం")
        fields = {
            "eligibility": ("eligibility", "Eligibility for", "కు అర్హతలు"),
            "required_documents": ("required_documents", "Required documents for", "కు కావాల్సిన పత్రాలు"),
            "benefits": ("benefits", "Benefits of", "ద్వారా వచ్చే లాభాలు"),
            "application_process": ("application_process", "How to apply for", "కు ఎలా దరఖాస్తు చేయాలి"),
        }
        key, english_prefix, telugu_suffix = fields.get(intent, ("description", "Details of", "వివరాలు"))
        context = str(scheme_data.get(key) or "").strip()
        if not context:
            return (f"Specific information about {name} is currently unavailable." if en
                    else f"{name} కు సంబంధించిన ఈ నిర్దిష్ట సమాచారం ప్రస్తుతం అందుబాటులో లేదు.")
        if en:
            return f"{english_prefix} {name}: {context}"
        return f"{name} {telugu_suffix}: {context}"
