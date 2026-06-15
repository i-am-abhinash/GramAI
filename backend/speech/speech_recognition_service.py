import speech_recognition as sr
import threading

class SpeechRecognitionService:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Set static initial threshold to avoid 1-second blocking initialization
        self.recognizer.energy_threshold = 400
        self.recognizer.dynamic_energy_threshold = True

    def listen_and_transcribe(self, language='te-IN', timeout=5, phrase_time_limit=10):
        """
        Listens to the microphone and transcribes speech.
        Returns the recognized text or an error message.
        """
        try:
            with self.microphone as source:
                print("Listening...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            
            print("Processing speech...")
            # Recognize speech using Google Web Speech API
            text = self.recognizer.recognize_google(audio, language=language)
            return {"success": True, "text": text}
            
        except sr.WaitTimeoutError:
            return {"success": False, "error": "Listening timed out. No speech detected."}
        except sr.UnknownValueError:
            return {"success": False, "error": "Sorry, I could not understand the audio."}
        except sr.RequestError as e:
            return {"success": False, "error": f"Could not request results; {e}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
