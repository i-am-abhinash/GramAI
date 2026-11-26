"""Phase 1 regression tests. Run from repository root with dependencies installed."""
import unittest
from unittest.mock import Mock, patch
from mysql.connector import Error

from backend.repositories.scheme_repository import SchemeRepository
from backend.services.government_information_service import GovernmentInformationService
from backend.services.sync_service import GovernmentSchemeSyncService


class VerifiedKnowledgeTests(unittest.TestCase):
    def test_sync_never_claims_success(self):
        result = GovernmentSchemeSyncService().run_sync()
        self.assertFalse(result["success"])
        self.assertEqual(result["imported"], 0)
        self.assertEqual(result["updated"], 0)

    @patch("backend.repositories.scheme_repository.db")
    def test_repository_only_reads_verified_view(self, db):
        conn = db.connect.return_value
        cursor = conn.cursor.return_value
        cursor.fetchall.return_value = []
        self.assertEqual(SchemeRepository().get_all_schemes(), [])
        sql = cursor.execute.call_args.args[0]
        self.assertIn("verified_scheme_answers", sql)
        self.assertNotIn("imported_schemes", sql)
        conn.close.assert_called_once()

    @patch("backend.repositories.scheme_repository.db")
    def test_missing_migration_fails_closed(self, db):
        conn = db.connect.return_value
        cursor = conn.cursor.return_value
        cursor.execute.side_effect = Error("View does not exist")
        self.assertEqual(SchemeRepository().get_all_schemes(), [])
        conn.close.assert_called_once()

    def test_empty_verified_knowledge_never_answers_from_legacy_cache(self):
        service = GovernmentInformationService()
        service.retrieval = Mock()
        service.retrieval.retrieve_schemes.return_value = []
        service.unanswered_repo = Mock()
        service.query_log_repo = Mock()
        service.rag = Mock()
        result = service.process_query("When will the next farmer subsidy be released?", "en")
        self.assertIn("do not have verified information", result["text"])
        service.rag.generate_response.assert_not_called()
        service.unanswered_repo.record_query.assert_called_once()
        self.assertFalse(service.query_log_repo.log_query.call_args.kwargs["is_successful"])

    def test_low_score_does_not_generate_answer(self):
        service = GovernmentInformationService()
        service.retrieval = Mock()
        service.retrieval.retrieve_schemes.return_value = [(8.0, {"name": "Unrelated"})]
        service.unanswered_repo = Mock()
        service.query_log_repo = Mock()
        service.rag = Mock()
        result = service.process_query("unrelated question", "en")
        self.assertIn("do not have verified information", result["text"])
        service.rag.generate_response.assert_not_called()


if __name__ == "__main__":
    unittest.main()
