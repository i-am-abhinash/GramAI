import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class NLPService:
    def __init__(self):
        # 1. Intent Categories
        self.intent_keywords = {
            "eligibility": ["eligibility", "eligible", "who can", "age limit", "qualification", "అర్హతలు", "అర్హత"],
            "required_documents": ["documents", "proof", "certificates", "aadhaar", "ration card", "పత్రాలు", "డాక్యుమెంట్స్"],
            "benefits": ["benefits", "money", "amount", "rupees", "how much", "లాభాలు", "డబ్బులు"],
            "application_process": ["apply", "process", "where", "how to", "register", "అప్లై", "దరఖాస్తు"],
            "scholarship_information": ["scholarship", "fee", "student", "study", "స్కాలర్షిప్", "చదువు"],
            "scheme_search": ["search", "find", "list of", "వెతుకు"],
        }
        
        # 2. Entity Categories
        self.entity_keywords = {
            "pension": ["pension", "old age", "widow", "disabled", "పెన్షన్", "పింఛను"],
            "ration": ["ration", "rice", "dal", "groceries", "రేషన్"],
            "scholarship": ["scholarship", "school", "college", "fee", "స్కాలర్షిప్"],
            "housing": ["housing", "house", "home", "plot", "ఇల్లు", "స్థలం"],
            "health": ["health", "hospital", "treatment", "surgery", "ఆరోగ్య", "వైద్యం"],
            "education": ["education", "study", "school", "student", "చదువు"],
            "welfare": ["welfare", "scheme", "పథకం"]
        }
        
        self.stop_words = set([
            "i", "need", "want", "help", "with", "for", "the", "a", "an", "is", "are", "what", "how", "where", "can", "get", "information", "about", "details",
            "నాకు", "కావాలి", "గురించి", "చెప్పు", "వివరాలు", "ఎలా", "ఏమిటి"
        ])
        
        self.vectorizer = TfidfVectorizer()

    def extract_keywords(self, text):
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [w for w in words if w not in self.stop_words]
        return keywords

    def detect_intent(self, text):
        text_lower = text.lower()
        best_intent = "scheme_information" # Default intent
        max_matches = 0
        
        for intent, kw_list in self.intent_keywords.items():
            matches = sum(1 for kw in kw_list if kw in text_lower)
            if matches > max_matches:
                max_matches = matches
                best_intent = intent
                
        return best_intent

    def detect_entity(self, text):
        text_lower = text.lower()
        best_entity = "welfare" # Default entity
        max_matches = 0
        
        for entity, kw_list in self.entity_keywords.items():
            matches = sum(1 for kw in kw_list if kw in text_lower)
            if matches > max_matches:
                max_matches = matches
                best_entity = entity
                
        return best_entity

    def rank_schemes(self, query, schemes):
        if not schemes:
            return []
            
        documents = []
        for s in schemes:
            doc = f"{s.get('name', '')} {s.get('category', '')} {s.get('description', '')} {s.get('benefits', '')} {s.get('keywords', '')}"
            documents.append(doc)
            
        # Strip stop words from the query to avoid matching irrelevant terms like "గురించి"
        keywords = self.extract_keywords(query)
        processed_query = " ".join(keywords)
        documents.append(processed_query)
        
        try:
            tfidf_matrix = self.vectorizer.fit_transform(documents)
            cosine_similarities = cosine_similarity(tfidf_matrix[-1:], tfidf_matrix[:-1]).flatten()
            
            results = []
            for idx, score in enumerate(cosine_similarities):
                pct_score = round(float(score) * 100, 2)
                results.append((pct_score, schemes[idx]))
                
            results.sort(key=lambda x: x[0], reverse=True)
            return results
        except ValueError:
            return [(0.0, s) for s in schemes]
