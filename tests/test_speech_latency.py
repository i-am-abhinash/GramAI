"""Regression checks for low-latency speech, without network or sound hardware."""
import threading
import os
import tempfile
import unittest
from unittest.mock import patch
from backend.speech import text_to_speech_service as speech

from backend.speech.text_to_speech_service import TextToSpeechService, split_for_playback


class SpeechLatencyTests(unittest.TestCase):
    def test_forbidden_provider_skips_alternate_and_future_requests(self):
        class Forbidden(Exception):
            status = 403

        def fail(*args, **kwargs):
            raise Forbidden()

        def save(path):
            with open(path, "wb") as f:
                f.write(b"mock audio")

        with tempfile.TemporaryDirectory() as directory, patch.object(speech, "_EDGE_RETRY_AT", 0.0), patch.dict(os.environ, {"GRAMAI_TTS_ENGINE": "auto", "GRAMAI_ALLOW_GTTS": "1"}), patch.object(speech.edge_tts, "Communicate", side_effect=fail) as edge, patch("gtts.gTTS") as google, patch.object(speech, "ffmpeg_executable", return_value=None):
            google.return_value.save.side_effect = save
            first = TextToSpeechService()._generate_segment("test", "en", speech.VOICES["en"], directory, 0)
            second = TextToSpeechService()._generate_segment("test again", "en", speech.VOICES["en"], directory, 1)
            self.assertEqual(first[1], "gTTS")
            self.assertEqual(second[1], "gTTS")
            edge.assert_called_once()
            self.assertEqual(google.call_count, 2)

    def test_explicit_gtts_mode_skips_edge(self):
        with patch.dict(os.environ, {"GRAMAI_TTS_ENGINE": "gtts"}):
            self.assertFalse(speech.edge_available())

    def test_short_text_is_one_segment(self):
        self.assertEqual(split_for_playback("PM-KISAN benefits."), ["PM-KISAN benefits."])

    def test_long_text_preserves_words_and_amounts(self):
        text = "పీఎం కిసాన్ పథకం. " + "అర్హులైన రైతులకు రూ.6,000 అందుతుంది. " * 20
        text = text.strip()
        chunks = split_for_playback(text)
        self.assertGreater(len(chunks), 1)
        self.assertLessEqual(len(chunks[0]), 160)
        self.assertEqual(" ".join(chunks), text)
        self.assertEqual(" ".join(chunks).count("రూ.6,000"), 20)

    def test_long_sentence_preserves_text(self):
        text = " ".join(["eligibility"] * 80)
        chunks = split_for_playback(text)
        self.assertEqual(" ".join(chunks), text)
        self.assertLessEqual(len(chunks[0]), 160)

    @patch("backend.speech.text_to_speech_service.pygame.mixer")
    def test_next_segment_prepared_during_first_playback(self, mixer):
        service = TextToSpeechService()
        next_started = threading.Event()
        release_next = threading.Event()
        played = []
        text = "This is the first sentence. " + "This is a later sentence. " * 20
        def generate(spoken, lang, voice, directory, index, preferred_engine=None):
            if index == 1:
                next_started.set()
                release_next.wait(2)
            return str(index), "edge-tts", voice
        def play(path, first_started=None):
            played.append(path)
            if path == "0":
                try:
                    self.assertTrue(next_started.wait(2))
                finally:
                    release_next.set()
            return True
        with patch.object(service, "_generate_segment", side_effect=generate), patch.object(service, "_play_segment", side_effect=play):
            self.assertTrue(service.speak(text, "en"))
        self.assertGreater(len(played), 1)
        self.assertEqual(played, [str(i) for i in range(len(played))])

    @patch("backend.speech.text_to_speech_service.pygame.mixer")
    def test_cancel_stops_remaining_playback(self, mixer):
        service = TextToSpeechService()
        text = "First sentence. " + "More information. " * 30
        def play(path, first_started=None):
            service.stop()
            return False
        with patch.object(service, "_generate_segment", return_value=("audio.mp3","edge-tts","voice")), patch.object(service, "_play_segment", side_effect=play) as playback:
            self.assertFalse(service.speak(text, "en"))
            playback.assert_called_once()


if __name__ == "__main__":
    unittest.main()
