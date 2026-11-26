import unittest
from unittest.mock import Mock
from backend.services.retrieval_service import RetrievalService, normalized
from backend.services.official_knowledge_service import BUNDLE, FIELDS
import json


class OfficialKnowledgeTests(unittest.TestCase):
    def test_bilingual_bundle_complete(self):
        bundle = json.loads(BUNDLE.read_text(encoding="utf-8"))
        self.assertEqual(len(bundle["schemes"]),2)
        for item in bundle["schemes"]:
            for lang in ("te","en"):
                self.assertTrue(all(item[lang][f].strip() for f in ("name",)+FIELDS))
            self.assertEqual(set(item["evidence"]),set(FIELDS))

    def test_only_named_scheme(self):
        service = RetrievalService()
        service.scheme_repo = Mock()
        scheme = {"name":"PM-KISAN","te_name":"పీఎం కిసాన్","aliases":["PM KISAN"]}
        service.scheme_repo.get_all_schemes.return_value = [scheme]
        self.assertEqual(service.retrieve_schemes("farmer money","welfare"),[])
        self.assertEqual(service.retrieve_schemes("PM-KISAN eligibility","welfare"),[(100.0,scheme)])
        self.assertEqual(service.retrieve_schemes("పీఎం కిసాన్ అర్హత","welfare"),[(100.0,scheme)])
        self.assertEqual(service.retrieve_schemes("PM KISANOTHER","welfare"),[])


if __name__ == "__main__":
    unittest.main()
