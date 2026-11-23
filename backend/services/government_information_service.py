from backend.services.faq_service import FaqService
from backend.repositories.unanswered_query_repository import UnansweredQueryRepository
from backend.repositories.query_log_repository import QueryLogRepository
from backend.services.nlp_service import NLPService
from backend.services.retrieval_service import RetrievalService
from backend.services.rag_service import RAGService
from backend.services.cache_service import CacheService
from backend.database.mysql_connection import db

class GovernmentInformationService:
    def __init__(self):
        self.faq_service = FaqService()
        self.unanswered_repo = UnansweredQueryRepository()
        self.query_log_repo = QueryLogRepository()
        self.nlp = NLPService()
        self.retrieval = RetrievalService()
        self.rag = RAGService()
        self.cache = CacheService()
        
    def process_query(self, query, language='te'):
        """
        RAG Architecture Implementation.
        Pipeline: Intent/Entity Detection -> Retrieval -> Context Build -> RAG Generate
        """
        language = 'en' if str(language).lower().startswith('en') else 'te'
        # Cache both the question and output language; never reuse a Telugu answer in English.
        cache_key = f'{language}:{query}'
        # 1. Check LRU Cache First
        cached_result = self.cache.get(cache_key)
        if cached_result:
            # We must log the query hit even if it's from memory cache
            intent = self.nlp.detect_intent(query)
            entity = self.nlp.detect_entity(query)
            kw_str = ", ".join(self.nlp.extract_keywords(query))
            self._log_query(query, intent, entity, kw_str, 100.0, cached_result, True, "LRU Cache")
            return {"type": "ANSWER", "text": cached_result, "source": {"name": "Memory Cache", "url": "", "date": ""}}

        # 2. NLP Preprocessing (Intent & Entity Detection)
        intent = self.nlp.detect_intent(query)
        entity = self.nlp.detect_entity(query)
        keywords = self.nlp.extract_keywords(query)
        kw_str = ", ".join(keywords)

        # 3. Check FAQ
        faq_answer = self.faq_service.get_answer(query)
        if faq_answer:
            faq_answer = self._localize(faq_answer, language)
            self._log_query(query, intent, entity, kw_str, 100.0, faq_answer, True, "FAQ")
            self.cache.set(cache_key, faq_answer)
            return {"type": "ANSWER", "text": faq_answer, "source": {"name": "GramAI FAQ", "url": "", "date": ""}}
            
        # 4. Retrieval Engine (Semantic TF-IDF on specific category)
        ranked_schemes = self.retrieval.retrieve_schemes(query, entity)
        
        if ranked_schemes:
            top_score, top_scheme = ranked_schemes[0]
            
            # Check Clarification Engine logic for ambiguity
            if len(ranked_schemes) > 1:
                second_score, second_scheme = ranked_schemes[1]
                if top_score > 10.0 and (top_score - second_score) < 5.0:
                    options = [s['name'] for score, s in ranked_schemes[:3] if score > 5.0]
                    if len(options) > 1:
                        return {
                            "type": "CLARIFICATION",
                            "options": options
                        }

            # Valid strong match
            if top_score > 5.0:
                # 5 & 6. Context Builder & AI Generation (RAG)
                answer = self.rag.generate_response(intent, top_scheme, language=language)
                answer = self._localize(answer, language)
                
                # Extract Source info
                source_data = {
                    "name": top_scheme.get("source_name", "Unknown Source"),
                    "url": top_scheme.get("source_url", ""),
                    "date": str(top_scheme.get("last_sync_date", ""))[:10]
                }

                self._log_query(query, intent, entity, kw_str, top_score, answer, True, "RAG Knowledge Base")
                self.cache.set(cache_key, answer) # Basic text caching for MVP
                return {"type": "ANSWER", "text": answer, "source": source_data}
                
        # 7. Fallback to Unanswered Queue
        self.unanswered_repo.record_query(query, intent, entity)
        fallback_msg = ("This information is not available right now. Please try again later." if language == "en"
                        else "ఈ సమాచారం ప్రస్తుతం అందుబాటులో లేదు. దయచేసి తర్వాత మళ్ళీ ప్రయత్నించండి.")
        self._log_query(query, intent, entity, kw_str, 0.0, fallback_msg, False, "Unanswered Fallback")
        return {"type": "ANSWER", "text": fallback_msg, "source": {"name": "", "url": "", "date": ""}}

    @staticmethod
    def _localize(text, language):
        """Translate Telugu source content for English mode when necessary.

        Translation is optional/network-dependent. On failure, clearly identify the
        untranslated content instead of silently presenting it as an English answer.
        """
        if language != "en" or not text or not any("\\u0c00" <= ch <= "\\u0c7f" for ch in text):
            return text
        try:
            from deep_translator import GoogleTranslator
            return GoogleTranslator(source="auto", target="en").translate(text) or text
        except Exception as exc:
            print(f"English translation unavailable: {exc}")
            return "English translation is currently unavailable. Original information: " + text

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
