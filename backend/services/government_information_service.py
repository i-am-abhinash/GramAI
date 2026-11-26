from backend.repositories.unanswered_query_repository import UnansweredQueryRepository
from backend.repositories.query_log_repository import QueryLogRepository
from backend.services.nlp_service import NLPService
from backend.services.retrieval_service import RetrievalService
from backend.services.rag_service import RAGService

class GovernmentInformationService:
    def __init__(self):
        self.unanswered_repo = UnansweredQueryRepository()
        self.query_log_repo = QueryLogRepository()
        self.nlp = NLPService()
        self.retrieval = RetrievalService()
        self.rag = RAGService()
        
    def process_query(self, query, language='te'):
        """
        RAG Architecture Implementation.
        Pipeline: Intent/Entity Detection -> Retrieval -> Context Build -> RAG Generate
        """
        language = 'en' if str(language).lower().startswith('en') else 'te'
        # Re-read verified knowledge on every request. Legacy FAQs and caches are not trusted.
        # 2. NLP Preprocessing (Intent & Entity Detection)
        intent = self.nlp.detect_intent(query)
        entity = self.nlp.detect_entity(query)
        keywords = self.nlp.extract_keywords(query)
        kw_str = ", ".join(keywords)

        # 4. Retrieval Engine (Semantic TF-IDF on specific category)
        ranked_schemes = self.retrieval.retrieve_schemes(query, entity)
        
        if ranked_schemes:
            top_score, top_scheme = ranked_schemes[0]
            
            # Check Clarification Engine logic for ambiguity
            if len(ranked_schemes) > 1:
                second_score, second_scheme = ranked_schemes[1]
                if top_score >= 20.0 and (top_score - second_score) < 10.0:
                    options = [s.get('te_name',s['name']) if language == 'te' else s['name'] for score, s in ranked_schemes[:3] if score >= 15.0]
                    if len(options) > 1:
                        return {
                            "type": "CLARIFICATION",
                            "options": options
                        }

            # Valid strong match
            if top_score >= 35.0:
                result = self.answer_scheme(intent, top_scheme, language)
                self._log_query(query, intent, entity, kw_str, top_score, result["text"], True, "RAG Knowledge Base")
                return result
                
        # 7. Fallback to Unanswered Queue
        self.unanswered_repo.record_query(query, intent, entity)
        fallback_msg = ("I do not have verified information for this question yet. Please check with the relevant government office." if language == "en"
                        else "ఈ ప్రశ్నకు సంబంధించిన నిర్ధారించిన సమాచారం ఇంకా నా దగ్గర లేదు. సంబంధిత ప్రభుత్వ కార్యాలయంలో అడిగి తెలుసుకోండి.")
        self._log_query(query, intent, entity, kw_str, 0.0, fallback_msg, False, "Unanswered Fallback")
        return {"type": "ANSWER", "text": fallback_msg, "source": {"name": "", "url": "", "date": ""}}

    def answer_scheme(self, intent, scheme, language="te"):
        """Render a row obtained from the current verified knowledge view."""
        top_scheme = dict(scheme)
        if language == "te":
            for field in ("name", "description", "eligibility", "required_documents", "benefits", "application_process"):
                top_scheme[field] = top_scheme.get("te_" + field, "")
        return {"type": "ANSWER", "text": self.rag.generate_response(intent, top_scheme, language=language),
                "source": {"name": top_scheme.get("source_name", ""), "url": top_scheme.get("source_url", ""),
                           "date": str(top_scheme.get("last_verified_date", ""))[:10],
                           "scheme_title": top_scheme.get("name", ""), "scheme_desc": top_scheme.get("description", ""),
                           "scheme_elig": top_scheme.get("eligibility", "")}}

    def record_public_answer(self, intent, scheme, result):
        """Log only a canonical public scheme question, not the citizen's personal reply."""
        labels = {"eligibility": "eligibility", "required_documents": "documents",
                  "benefits": "benefits", "application_process": "how to apply"}
        query = scheme["name"] + " " + labels.get(intent, "details")
        self._log_query(query, intent, "welfare", "", 100.0, result["text"], True, "RAG Knowledge Base")

    def _log_query(self, query, intent, entity, keywords, score, response, is_successful, response_source):
        self.query_log_repo.log_query(
            query_text=query,
            intent=intent,
            entity=entity,
            keywords=keywords,
            match_score=score,
            response_text=response,
            is_successful=is_successful,
            response_source=response_source
        )
