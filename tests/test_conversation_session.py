"""Conversation regression tests using a fake verified repository."""
import json
import unittest
from types import SimpleNamespace
from unittest.mock import Mock
from backend.services.conversation_service import ConversationSession, parse_age, _BUNDLE

def make_scheme(key, ident):
    item = next(x for x in json.loads(_BUNDLE.read_text(encoding="utf-8"))["schemes"] if x["key"] == key)
    row = {"id": ident, "source_url": item["source_url"], "aliases": [a[1] for a in item["aliases"]]}
    for lang, prefix in (("en", ""), ("te", "te_")):
        row.update({prefix + k: v for k, v in item[lang].items()})
        row[prefix + "eligibility"] += "\n" + item[lang]["exclusions"]
    return row

class ConversationTests(unittest.TestCase):
    def setUp(self):
        self.rows = [make_scheme("pm-kisan", 1), make_scheme("pmjjby", 2)]
        self.gov = Mock()
        self.gov.retrieval.scheme_repo.get_all_schemes.side_effect = lambda: self.rows
        self.gov.nlp.detect_intent.side_effect = lambda q: "application_process" if "apply" in q else "scheme_information"
        self.gov.nlp.detect_entity.return_value = "welfare"
        self.gov.answer_scheme.side_effect = lambda intent, scheme, language: {"type":"ANSWER","text":intent + ":" + str(scheme["id"]),"source":{}}
        self.gov.process_query.return_value = {"type":"ANSWER","text":"unavailable","source":{}}
        self.session = ConversationSession()

    def ask(self, text):
        return self.session.process(self.gov, text, "en")

    def test_context_and_switch(self):
        self.ask("PM KISAN")
        self.assertEqual(self.ask("documents")["text"], "required_documents:1")
        self.ask("PMJJBY")
        self.assertEqual(self.ask("benefits")["text"], "benefits:2")

    def test_guided_new_enrolment(self):
        self.assertIn("How old", self.ask("apply PMJJBY")["text"])
        self.assertIn("individual account", self.ask("35")["text"])
        self.assertIn("premium", self.ask("yes")["text"])
        result = self.ask("yes")
        self.assertIn("not final approval", result["text"])
        self.assertIn("required_documents:2", result["text"])
        self.assertIsNone(self.session.age)
        self.gov.process_query.assert_not_called()
        self.gov.record_public_answer.assert_not_called()

    def test_age_outside_range(self):
        self.ask("apply PMJJBY")
        self.assertIn("18 to 50", self.ask("69")["text"])
        self.assertIsNone(self.session.awaiting)

    def test_expired_scheme(self):
        self.ask("apply PMJJBY")
        self.rows.pop()
        self.assertIn("no longer", self.ask("35")["text"])
        self.assertIsNone(self.session.scheme_id)

    def test_changed_rules_disable_pilot(self):
        self.rows[1]["eligibility"] += " changed"
        self.assertEqual(self.ask("apply PMJJBY")["text"], "application_process:2")
        self.assertIsNone(self.session.awaiting)

    def test_stop_clears_session(self):
        self.ask("apply PMJJBY")
        self.ask("35")
        self.assertEqual(self.ask("stop")["type"], "END")
        self.assertIsNone(self.session.age)
        self.assertIsNone(self.session.scheme_id)

    def test_clarification_keeps_intent(self):
        self.assertEqual(self.ask("apply PM KISAN or PMJJBY")["type"], "CLARIFICATION")
        self.assertIn("How old", self.ask("2")["text"])

    def test_age_parsing(self):
        self.assertEqual(parse_age("౩౫"), 35)
        self.assertEqual(parse_age("sixty nine"), 69)
        self.assertIsNone(parse_age("1234567890"))

if __name__ == "__main__":
    unittest.main()
