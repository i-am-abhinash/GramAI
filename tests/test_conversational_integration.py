"""Comprehensive integration test for Conversational Intelligence features in GramAI."""
import os
import unittest
from unittest.mock import Mock, patch
from PyQt6.QtWidgets import QApplication

# Ensure QApplication exists for QObject/QThread signals
app = QApplication.instance() or QApplication([])

from backend.main_controller import MainController
from backend.services.conversation_service import ConversationSession
from backend.speech import text_to_speech_service as speech


class ConversationalIntelligenceIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.controller = MainController()
        # Mock TTS so audio hardware is not needed during testing
        self.controller.tts_service = Mock()

    def test_voice_settings_preserved(self):
        """Verify local voice speed settings and bundled FFmpeg detection."""
        self.assertEqual(speech.NATIVE_RATE, "+60%")
        self.assertEqual(speech.FALLBACK_TEMPO, 1.60)
        # Default engine must be gTTS
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(speech.edge_available())
        # Neural engine must remain available as optional
        with patch.dict(os.environ, {"GRAMAI_TTS_ENGINE": "edge"}):
            self.assertTrue(speech.edge_available())
        # Bundled FFmpeg executable must be detected
        exe = speech.ffmpeg_executable()
        self.assertIsNotNone(exe)
        self.assertTrue(os.path.exists(exe))

    def test_contextual_followups_and_switching(self):
        """Verify scheme context is retained across follow-up queries and switches cleanly."""
        session = ConversationSession()
        gov = Mock()
        scheme_1 = {"id": 1, "name": "PM-KISAN", "aliases": ["pm kisan", "పీఎం కిసాన్"]}
        scheme_2 = {"id": 2, "name": "PMJJBY", "aliases": ["pmjjby", "జీవన జ్యోతి"]}

        gov.retrieval.scheme_repo.get_all_schemes.return_value = [scheme_1, scheme_2]
        gov.nlp.detect_intent.side_effect = lambda q: "required_documents" if "document" in q else "benefits" if "benefit" in q else "scheme_information"
        gov.nlp.detect_entity.return_value = "welfare"
        gov.answer_scheme.side_effect = lambda intent, scheme, language: {
            "type": "ANSWER",
            "text": f"{intent} for {scheme['name']}",
            "source": {}
        }

        # Query 1: Initial scheme inquiry
        res1 = session.process(gov, "PM KISAN", "en")
        self.assertEqual(session.scheme_id, 1)

        # Query 2: Contextual follow-up without naming the scheme
        res2 = session.process(gov, "documents", "en")
        self.assertEqual(session.scheme_id, 1)
        self.assertEqual(res2["text"], "required_documents for PM-KISAN")

        # Query 3: Switch context to a different scheme
        res3 = session.process(gov, "PMJJBY", "en")
        self.assertEqual(session.scheme_id, 2)

        # Query 4: Follow-up on newly switched scheme
        res4 = session.process(gov, "benefits", "en")
        self.assertEqual(session.scheme_id, 2)
        self.assertEqual(res4["text"], "benefits for PMJJBY")

    def test_session_reset_manual_and_stop_command(self):
        """Verify session resets cleanly upon home navigation and stop phrases."""
        self.controller.session_active = True
        self.controller.session.scheme_id = 42
        self.controller._silence_count = 1

        # Test manual reset
        self.controller.reset_session()
        self.assertFalse(self.controller.session_active)
        self.assertIsNone(self.controller.session.scheme_id)
        self.assertEqual(self.controller._silence_count, 0)

        # Test conversational 'stop' trigger
        session = ConversationSession()
        session.scheme_id = 42
        gov = Mock()
        stop_result = session.process(gov, "stop", "en")
        self.assertEqual(stop_result["type"], "END")
        self.assertIsNone(session.scheme_id)

        # Test Telugu stop trigger
        session.scheme_id = 42
        telugu_stop = session.process(gov, "ధన్యవాదాలు", "te")
        self.assertEqual(telugu_stop["type"], "END")
        self.assertIsNone(session.scheme_id)

    def test_inactivity_timeout_and_reminder_flow(self):
        """Verify first silence triggers reminder prompt and second silence returns home."""
        self.controller.session_active = True
        self.controller._silence_count = 0

        # First silence timeout
        mock_sender = Mock()
        with patch.object(self.controller, "sender", return_value=mock_sender), \
             patch.object(self.controller, "worker", mock_sender):
            mock_sender._is_cancelled = False
            self.controller._handle_error("Listening timed out. No speech detected.")

        self.assertEqual(self.controller._silence_count, 1)
        self.assertEqual(self.controller._after_worker, "reminder")

        # Second consecutive silence timeout
        with patch.object(self.controller, "sender", return_value=mock_sender), \
             patch.object(self.controller, "worker", mock_sender):
            self.controller._handle_error("Listening timed out. No speech detected.")

        self.assertEqual(self.controller._after_worker, "home")

    def test_cancellation_and_worker_replacement(self):
        """Verify _cancel_active stops TTS and workers, and queues replacement safely."""
        mock_worker = Mock()
        self.controller.worker = mock_worker
        self.controller.session_active = True

        # Call cancel
        self.controller._cancel_active()
        mock_worker.stop.assert_called_once()
        self.controller.tts_service.stop.assert_called_once()

        # Verify replacement factory queueing
        replacement_factory = Mock()
        self.controller._launch(replacement_factory)
        self.assertEqual(self.controller._pending_start, replacement_factory)


if __name__ == "__main__":
    unittest.main()
