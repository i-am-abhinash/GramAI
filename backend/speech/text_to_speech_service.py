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
        if not text or not text.strip():
            return False
        self._is_cancelled = False
        voice = VOICES["en" if str(language).lower().startswith("en") else "te"]
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
                        await edge_tts.Communicate(text, voice, rate="-5%").save(path)
                    asyncio.run(generate())
                    if os.path.exists(path) and os.path.getsize(path) > 0:
                        audio_generated = True
                except Exception as exc:
                    print(f"edge-tts failed ({exc}), attempting fallback...")

                if not audio_generated and not self._is_cancelled:
                    try:
                        import gtts
                        tts = gtts.gTTS(text=text, lang="te" if voice.startswith("te") else "en")
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
