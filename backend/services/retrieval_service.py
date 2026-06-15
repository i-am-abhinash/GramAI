from backend.repositories.scheme_repository import SchemeRepository
from backend.services.nlp_service import NLPService

class RetrievalService:
    """Retrieves relevant schemes based on detected entity and semantic matching."""
    
    def __init__(self):
        self.scheme_repo = SchemeRepository()
        self.nlp_service = NLPService()
        
    def retrieve_schemes(self, query_text, entity):
        """
        1. Fetch candidates from DB filtered by entity category.
        2. Rank them using semantic matching.
        """
        # Step 1: Pre-filter candidates by Entity
        if entity and entity != "welfare":
            candidates = self.scheme_repo.get_schemes_by_category(entity)
            if not candidates:
                # Fallback to all if no specific entity match found in DB
                candidates = self.scheme_repo.get_all_schemes()
        else:
            candidates = self.scheme_repo.get_all_schemes()
            
        # Step 2: Semantic relevance ranking
        ranked_results = self.nlp_service.rank_schemes(query_text, candidates)
        
        return ranked_results
