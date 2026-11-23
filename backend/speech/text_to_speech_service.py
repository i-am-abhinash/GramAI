"""Conversational Telugu / Indian English voice output for GramAI.

Uses neural TTS for natural pronunciation. Keep spoken wording faithful to the
answer; avoid inventing benefits, eligibility rules, or required documents.
"""
import asyncio
import os
import re
import tempfile
import threading

import edge_tts
import pygame

_AUDIO_LOCK = threading.Lock()
VOICES = {"te": "te-IN-ShrutiNeural", "en": "en-IN-NeerjaNeural"}
TELUGU_RE = re.compile(r"[\u0c00-\u0c7f]")


def prepare_for_speech(text, language="te"):
    """Make a written answer easier to listen to without changing its facts."""
    spoken = re.sub(r"\s+", " ", str(text or "")).strip()
    # Do not read markdown decoration aloud.
    spoken = re.sub(r"(?m)\*\*|__|\x60", "", spoken)
    spoken = re.sub(r"\s*([।.!?])\s*", r"\1 ", spoken).strip()
    if language == "te":
        # Replace only stock formal phrases with familiar spoken equivalents.
        replacements = (
            ("దయచేసి", ""),
            ("సమర్పించవలెను", "ఇవ్వాలి"),
            ("సమర్పించాలి", "ఇవ్వాలి"),
            ("దరఖాస్తు చేసుకొనవలెను", "అప్లై చేయాలి"),
            ("దరఖాస్తు చేసుకోవాలి", "అప్లై చేయాలి"),
            ("ధృవపత్రాలు", "పత్రాలు"),
            ("అందుబాటులో లేదు", "ఇప్పుడు సమాచారం లేదు"),
            ("మళ్ళీ ప్రయత్నించండి", "మళ్లీ అడగండి"),
        )
        for original, conversational in replacements:
            spoken = spoken.replace(original, conversational)
        spoken = re.sub(r"\s+", " ", spoken).strip()
    return spoken


class TextToSpeechService:
    def __init__(self):
        self.voice = VOICES["te"]
        self._is_cancelled = False

    def stop(self):
        """Stop current playback."""
        self._is_cancelled = True
        try:
            if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
        except Exception:
            pass

    def speak(self, text, language="te"):
        if not text or not str(text).strip():
            return False
        self._is_cancelled = False
        lang = "en" if str(language).lower().startswith("en") else "te"
        voice = VOICES[lang]
        spoken = prepare_for_speech(text, lang)
        path = None
        try:
            with _AUDIO_LOCK:
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                    path = f.name
                
                audio_generated = False
                try:
                    async def generate():
                        rate = "-10%" if lang == "te" else "-4%"
                        await edge_tts.Communicate(spoken, voice, rate=rate).save(path)
                    asyncio.run(generate())
                    if os.path.exists(path) and os.path.getsize(path) > 0:
                        audio_generated = True
                except Exception as exc:
                    print(f"edge-tts failed ({exc}), attempting fallback...")

                if not audio_generated and not self._is_cancelled:
                    try:
                        import gtts
                        tts = gtts.gTTS(text=spoken, lang="te" if voice.startswith("te") else "en")
                        tts.save(path)
                        if os.path.exists(path) and os.path.getsize(path) > 0:
                            audio_generated = True
                    except Exception as exc:
                        print(f"gTTS fallback error: {exc}")

                if not audio_generated or self._is_cancelled:
                    return False

                pygame.mixer.music.load(path)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy() and not self._is_cancelled:
                    pygame.time.Clock().tick(20)
                if self._is_cancelled and pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
                pygame.mixer.music.unload()
            return not self._is_cancelled
        except Exception as exc:
            print(f"TTS Error ({voice}): {exc}")
            return False
        finally:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass
