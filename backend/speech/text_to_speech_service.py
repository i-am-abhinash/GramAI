import os
import pygame
import tempfile
import edge_tts
import asyncio

class TextToSpeechService:
    def __init__(self):
        # Initialize pygame mixer
        pygame.mixer.init()
        # te-IN-MohanNeural is the Microsoft Azure Telugu male voice
        self.voice = "te-IN-MohanNeural"
        self._is_cancelled = False

    def stop(self):
        """Stop current playback."""
        self._is_cancelled = True
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()

    def speak(self, text, language='te'):
        """
        Synthesizes text to speech using edge-tts (male voice) and plays it using pygame.
        """
        self._is_cancelled = False
        try:
            # Save to a temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            temp_path = temp_file.name
            temp_file.close()
            
            # Generate TTS audio: try edge-tts first, fallback to gTTS
            audio_generated = False
            try:
                communicate = edge_tts.Communicate(text, self.voice)
                asyncio.run(communicate.save(temp_path))
                if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                    audio_generated = True
            except Exception as e:
                print(f"edge-tts failed ({e}), falling back to gTTS...")

            if not audio_generated and not self._is_cancelled:
                try:
                    import gtts
                    tts = gtts.gTTS(text=text, lang=language)
                    tts.save(temp_path)
                    if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                        audio_generated = True
                except Exception as e:
                    print(f"gTTS fallback error: {e}")

            if not audio_generated or self._is_cancelled:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                return False

            # Load and play the audio file
            pygame.mixer.music.load(temp_path)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy() and not self._is_cancelled:
                pygame.time.Clock().tick(10)
                
            if self._is_cancelled and pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                
            # Unload the music and delete the temp file
            pygame.mixer.music.unload()
            try:
                os.remove(temp_path)
            except Exception as e:
                print(f"Warning: Could not delete temp audio file {temp_path}: {e}")
                
            return not self._is_cancelled
            
        except Exception as e:
            print(f"TTS Error: {e}")
            return False
