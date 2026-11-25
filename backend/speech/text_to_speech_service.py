"""Conversational Telugu / Indian English voice output for GramAI.

Uses neural TTS for natural pronunciation. Keep spoken wording faithful to the
answer; avoid inventing benefits, eligibility rules, or required documents.
"""
import asyncio
import os
import re
import subprocess
import tempfile
import threading

import edge_tts
import pygame

_AUDIO_LOCK = threading.Lock()
VOICES = {"te": "te-IN-ShrutiNeural", "en": "en-IN-NeerjaNeural"}
ALTERNATE_VOICES = {"te": "te-IN-MohanNeural", "en": "en-IN-PrabhatNeural"}
NATIVE_RATE = "+60%"
FALLBACK_TEMPO = 1.60


def prepare_for_speech(text, language="te"):
    """Make a written answer easier to listen to without changing its facts."""
    spoken = str(text or "").strip()
    # Preserve paragraph and list boundaries as short spoken pauses.
    spoken = re.sub(r"(?m)^\s*(?:[-*•]|\d+[.)])\s+", "", spoken)
    spoken = re.sub(r"(?m)^\s*#{1,6}\s+", "", spoken)
    spoken = re.sub(r"(?<![.!?।])\s*\n+", ". ", spoken)
    spoken = re.sub(r"\s+", " ", spoken).strip()
    # Do not read markdown decoration aloud.
    spoken = re.sub(r"(?m)\*\*|__|\x60", "", spoken)
    spoken = re.sub(r"\s*([।!?]|(?<!\d)\.|\.(?!\d))\s*", r"\1 ", spoken).strip()
    if language == "te":
        # Replace only stock formal phrases with familiar spoken equivalents.
        replacements = (
            ("దయచేసి", ""),
            ("సమర్పించవలెను", "ఇవ్వాలి"),
            ("సమర్పించాలి", "ఇవ్వాలి"),
            ("దరఖాస్తు చేసుకొనవలెను", "అప్లై చేయాలి"),
            ("దరఖాస్తు చేసుకోవాలి", "అప్లై చేయాలి"),
            ("ధృవపత్రాలు", "పత్రాలు"),
            ("ప్రస్తుతం అందుబాటులో లేదు", "ఇప్పుడు అందుబాటులో లేదు"),
            ("మళ్ళీ ప్రయత్నించండి", "మళ్లీ ప్రయత్నించండి"),
        )
        for original, conversational in replacements:
            spoken = spoken.replace(original, conversational)
        spoken = re.sub(r"\s+", " ", spoken).strip()
    return spoken


def ffmpeg_executable():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as exc:
        print(f"GramAI TTS: audio tempo unavailable ({exc}); install requirements.txt.")
        return None


def accelerate_audio(source, executable, tempo):
    """Time-stretch without intentionally changing the voice's pitch."""
    fd, output = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    try:
        subprocess.run(
            [executable, "-hide_banner", "-loglevel", "error", "-y",
             "-i", source, "-vn", "-af", f"atempo={tempo:.3f}", output],
            check=True, capture_output=True, timeout=120,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        if os.path.getsize(output) <= 44:
            raise RuntimeError("Empty accelerated audio")
        return output
    except Exception as exc:
        print(f"GramAI TTS: tempo processing failed ({exc}); preserving original audio.")
        try:
            os.remove(output)
        except OSError:
            pass
        return None


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
        voice = os.getenv("GRAMAI_TTS_VOICE_" + lang.upper(), VOICES[lang])
        spoken = prepare_for_speech(text, lang)
        path = None
        accelerated_path = None
        try:
            with _AUDIO_LOCK:
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                    path = f.name
                
                engine = None
                audio_generated = False
                # Prefer native neural prosody rather than speeding up finished audio.
                for candidate in dict.fromkeys((voice, ALTERNATE_VOICES[lang])):
                    if self._is_cancelled:
                        return False
                    try:
                        async def generate():
                            await edge_tts.Communicate(
                                spoken, candidate, rate=NATIVE_RATE
                            ).save(path)
                        asyncio.run(generate())
                        if not os.path.getsize(path):
                            raise RuntimeError("Empty neural audio")
                        audio_generated = True
                        engine = "edge-tts"
                        voice = candidate
                        break
                    except Exception as exc:
                        print(f"GramAI TTS: neural voice {candidate} failed: {exc}", flush=True)

                if not audio_generated and not self._is_cancelled and os.getenv("GRAMAI_ALLOW_GTTS", "1") == "1":
                    try:
                        import gtts
                        tts = gtts.gTTS(text=spoken, lang=lang, slow=False)
                        tts.save(path)
                        if os.path.exists(path) and os.path.getsize(path) > 0:
                            audio_generated = True
                            engine = "gTTS"
                    except Exception as exc:
                        print(f"gTTS fallback error: {exc}")

                if not audio_generated or self._is_cancelled:
                    return False

                # gTTS lacks a native rate setting; use moderate pitch-preserving tempo.
                if engine == "gTTS":
                    executable = ffmpeg_executable()
                    if executable:
                        accelerated_path = accelerate_audio(path, executable, FALLBACK_TEMPO)
                if self._is_cancelled:
                    return False

                if engine == "edge-tts":
                    print(f"GramAI TTS v4: {voice}, native rate {NATIVE_RATE}", flush=True)
                else:
                    applied = FALLBACK_TEMPO if accelerated_path else 1.0
                    print(f"GramAI TTS v4: gTTS fallback, tempo {applied:.2f}x", flush=True)
                pygame.mixer.music.load(accelerated_path or path)
                try:
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy() and not self._is_cancelled:
                        pygame.time.Clock().tick(20)
                finally:
                    if pygame.mixer.music.get_busy():
                        pygame.mixer.music.stop()
                    pygame.mixer.music.unload()
            return not self._is_cancelled
        except Exception as exc:
            print(f"TTS Error ({voice}): {exc}")
            return False
        finally:
            for temporary_path in (accelerated_path, path):
                if temporary_path and os.path.exists(temporary_path):
                    try:
                        os.remove(temporary_path)
                    except OSError:
                        pass
