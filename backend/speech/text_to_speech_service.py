"""Natural neural speech output for Telugu and Indian English."""
import asyncio
import os
import tempfile
import threading
import edge_tts
import pygame

_AUDIO_LOCK = threading.Lock()
VOICES = {"te": "te-IN-ShrutiNeural", "en": "en-IN-NeerjaNeural"}

class TextToSpeechService:
    def __init__(self):
        self.voice = VOICES["te"]

    def speak(self, text, language="te"):
        if not text or not text.strip():
            return False
        voice = VOICES["en" if str(language).lower().startswith("en") else "te"]
        path = None
        try:
            with _AUDIO_LOCK:
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                    path = f.name
                async def generate():
                    await edge_tts.Communicate(text, voice, rate="-5%").save(path)
                asyncio.run(generate())
                pygame.mixer.music.load(path)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(20)
                pygame.mixer.music.unload()
            return True
        except Exception as exc:
            print(f"TTS Error ({voice}): {exc}")
            return False
        finally:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass
