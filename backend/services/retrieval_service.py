"""Conservative named-scheme retrieval for the initial official knowledge base."""
import unicodedata
from backend.repositories.scheme_repository import SchemeRepository


def normalized(text):
    text = unicodedata.normalize("NFKC",str(text or "")).casefold()
    return " ".join("".join(c if c.isalnum() or unicodedata.category(c).startswith("M") else " " for c in text).split())


class RetrievalService:
    def __init__(self):
        self.scheme_repo = SchemeRepository()

    def retrieve_schemes(self,query_text,entity):
        # Search names in both languages across all verified categories.
        # Do not guess a scheme from broad terms like pension, money or farmer.
        q = " " + normalized(query_text) + " "
        matches = []
        for scheme in self.scheme_repo.get_all_schemes():
            aliases = [scheme["name"],scheme.get("te_name",""),*scheme.get("aliases",[])]
            if any(normalized(a) and " "+normalized(a)+" " in q for a in aliases):
                matches.append((100.0,scheme))
        return matches
