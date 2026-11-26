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
import time
from concurrent.futures import ThreadPoolExecutor

import edge_tts
import pygame

_AUDIO_LOCK = threading.Lock()
# Shared across text, voice and replay workers.
_EDGE_RETRY_AT = 0.0
_EDGE_COOLDOWN_SECONDS = 300


def edge_available():
    engine = os.getenv("GRAMAI_TTS_ENGINE", "gtts").strip().lower()
    return (engine in ("edge", "edge-tts", "neural", "azure", "auto")
            and time.monotonic() >= _EDGE_RETRY_AT)


def mark_edge_unavailable():
    global _EDGE_RETRY_AT
    _EDGE_RETRY_AT = time.monotonic() + _EDGE_COOLDOWN_SECONDS


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
    fd, output = tempfile.mkstemp(suffix=".wav", dir=os.path.dirname(source))
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


def split_for_playback(text, first_limit=160, later_limit=360):
    """Keep the full wording, but make the first audio request short.

    Prefer sentence or clause boundaries. Only split at whitespace, so
    Telugu combining characters, decimals and words remain intact.
    """
    remaining = str(text or "").strip()
    chunks = []
    while remaining:
        limit = first_limit if not chunks else later_limit
        if len(remaining) <= limit:
            chunks.append(remaining)
            break
        boundaries = [m.start() for m in re.finditer(r"(?<=[.!?।])\s+", remaining)
                      if m.start() <= limit]
        if boundaries:
            # A short first sentence is enough to begin playback.
            cut = boundaries[0] if not chunks else boundaries[-1]
        else:
            clauses = [m.start() for m in re.finditer(r"(?<=[,;:])\s+", remaining)
                       if limit // 2 <= m.start() <= limit]
            spaces = [m.start() for m in re.finditer(r"\s+", remaining)
                      if 0 < m.start() <= limit]
            if clauses:
                cut = clauses[-1]
            elif spaces:
                cut = spaces[-1]
            else:
                # Do not cut a single long token in half.
                match = re.search(r"\s+", remaining)
                cut = match.start() if match else len(remaining)
        chunks.append(remaining[:cut].strip())
        remaining = remaining[cut:].lstrip()
    return chunks


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

    def _generate_segment(self, spoken, lang, voice, directory, index, preferred_engine=None):
        """Generate a single segment, without touching the playback mixer."""
        path = os.path.join(directory, f"segment_{index}.mp3")
        if preferred_engine != "gTTS" and edge_available():
            for candidate in dict.fromkeys((voice, VOICES[lang], ALTERNATE_VOICES[lang])):
                if self._is_cancelled:
                    return None
                try:
                    async def generate():
                        await asyncio.wait_for(
                            edge_tts.Communicate(spoken, candidate, rate=NATIVE_RATE).save(path),
                            timeout=25,
                        )
                    asyncio.run(generate())
                    if not os.path.getsize(path):
                        raise RuntimeError("Empty neural audio")
                    return path, "edge-tts", candidate
                except Exception as exc:
                    status = getattr(exc, "status", None)
                    print(f"GramAI TTS: neural voice {candidate} failed ({type(exc).__name__}, HTTP {status})", flush=True)
                    if status in (401, 403, 429):
                        mark_edge_unavailable()
                        print("GramAI TTS: neural provider unavailable; using fallback for 5 minutes.", flush=True)
                        break

        if self._is_cancelled or os.getenv("GRAMAI_ALLOW_GTTS", "1") != "1":
            return None
        try:
            import gtts
            fallback_started = time.perf_counter()
            tts = gtts.gTTS(text=spoken, lang=lang, slow=False, timeout=15)
            tts.save(path)
            print(f"GramAI TTS: fallback download took {time.perf_counter() - fallback_started:.2f}s", flush=True)
            if not os.path.getsize(path):
                raise RuntimeError("Empty fallback audio")
            if self._is_cancelled:
                return None
            executable = ffmpeg_executable()
            accelerated = accelerate_audio(path, executable, FALLBACK_TEMPO) if executable else None
            return accelerated or path, "gTTS", voice
        except Exception as exc:
            print(f"gTTS fallback error: {exc}", flush=True)
            return None

    def _play_segment(self, path, first_started=None):
        if self._is_cancelled:
            return False
        pygame.mixer.music.load(path)
        try:
            if self._is_cancelled:
                return False
            pygame.mixer.music.play()
            if first_started is not None:
                print(f"GramAI TTS: first playback requested after {time.perf_counter() - first_started:.2f}s", flush=True)
            clock = pygame.time.Clock()
            while pygame.mixer.music.get_busy() and not self._is_cancelled:
                clock.tick(40)
            return not self._is_cancelled
        finally:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            pygame.mixer.music.unload()

    def speak(self, text, language="te"):
        if not text or not str(text).strip():
            return False
        self._is_cancelled = False
        started = time.perf_counter()
        lang = "en" if str(language).lower().startswith("en") else "te"
        voice = os.getenv("GRAMAI_TTS_VOICE_" + lang.upper(), VOICES[lang])
        chunks = split_for_playback(prepare_for_speech(text, lang))
        if not chunks:
            return False
        try:
            with _AUDIO_LOCK:
                if self._is_cancelled:
                    return False
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                # Keep one segment ahead of playback. The executor finishes
                # before the directory is removed, including on cancellation.
                with tempfile.TemporaryDirectory(prefix="gramai_tts_") as directory:
                    with ThreadPoolExecutor(max_workers=1) as executor:
                        future = executor.submit(self._generate_segment, chunks[0], lang, voice, directory, 0)
                        for index in range(len(chunks)):
                            generated = future.result()
                            if self._is_cancelled or not generated:
                                return False
                            path, engine, voice = generated
                            if index + 1 < len(chunks):
                                future = executor.submit(
                                    self._generate_segment, chunks[index + 1], lang, voice,
                                    directory, index + 1, engine,
                                )
                            if index == 0:
                                print(f"GramAI TTS v6: {engine}, {voice}, {len(chunks)} segment(s)", flush=True)
                            if not self._play_segment(path, started if index == 0 else None):
                                return False
            return not self._is_cancelled
        except Exception as exc:
            print(f"TTS Error ({voice}): {exc}", flush=True)
            return False
