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

    def speak(self, text, language='te'):
        """
        Synthesizes text to speech using edge-tts (male voice) and plays it using pygame.
        """
        try:
            # Save to a temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            temp_path = temp_file.name
            temp_file.close()
            
            # Generate TTS audio using edge-tts
            communicate = edge_tts.Communicate(text, self.voice)
            asyncio.run(communicate.save(temp_path))
            
            # Load and play the audio file
            pygame.mixer.music.load(temp_path)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
                
            # Unload the music and delete the temp file
            pygame.mixer.music.unload()
            try:
                os.remove(temp_path)
            except Exception as e:
                print(f"Warning: Could not delete temp audio file {temp_path}: {e}")
                
            return True
            
        except Exception as e:
            print(f"TTS Error: {e}")
            return False
