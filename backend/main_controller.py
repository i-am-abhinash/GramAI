from PyQt6.QtCore import QObject, pyqtSignal, QThread
from backend.speech.speech_recognition_service import SpeechRecognitionService
from backend.speech.text_to_speech_service import TextToSpeechService
from backend.services.government_information_service import GovernmentInformationService
from backend.services.feedback_service import FeedbackService

class VoiceWorker(QThread):
    """
    Background thread to handle blocking voice tasks.
    """
    # Signals to communicate with the main GUI thread
    listening_started = pyqtSignal()
    processing_started = pyqtSignal(str) # Passes the recognized text
    response_ready = pyqtSignal(str, str, dict) # Passes (question, response, source)
    clarification_needed = pyqtSignal(str, list) # Passes (question, options)
    error_occurred = pyqtSignal(str)
    playback_finished = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.speech_service = SpeechRecognitionService()
        self.gov_service = GovernmentInformationService()
        self.tts_service = TextToSpeechService()
        
    def run(self):
        # 1. Start Listening
        self.listening_started.emit()
        result = self.speech_service.listen_and_transcribe()
        
        if not result["success"]:
            self.error_occurred.emit(result["error"])
            return
            
        recognized_text = result["text"]
        
        # 2. Start Processing
        self.processing_started.emit(recognized_text)
        
        # 3. Fetch Answer (now returns a semantic matching dictionary)
        response_data = self.gov_service.process_query(recognized_text)
        
        if response_data["type"] == "CLARIFICATION":
            # 4a. Trigger Clarification Engine
            self.clarification_needed.emit(recognized_text, response_data["options"])
            # Speak the clarification prompt
            prompt = "మీకు ఈ పథకాలలో ఏది కావాలి? " + " లేదా ".join(response_data["options"])
            self.tts_service.speak(prompt)
            # Do not auto-restart mic here, waiting for UI interaction
        else:
            # 4b. Display and Speak Answer
            answer_text = response_data["text"]
            source = response_data.get("source", {})
            self.response_ready.emit(recognized_text, answer_text, source)
            self.tts_service.speak(answer_text)
            self.playback_finished.emit()

class MainController(QObject):
    """
    Orchestrates the MVC architecture and ties UI to Backend.
    """
    # UI signals exposed for app_window
    transition_to_listening = pyqtSignal()
    transition_to_processing = pyqtSignal(str)
    transition_to_response = pyqtSignal(str, str, dict)
    transition_to_clarification = pyqtSignal(str, list)
    transition_to_home = pyqtSignal()
    show_error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.worker = None
        self.tts_service = TextToSpeechService() # For replay functionality
        self.feedback_service = FeedbackService()

    def handle_feedback(self, query, response, is_helpful):
        self.feedback_service.record_feedback(query, response, is_helpful)

    def handle_mic_clicked(self):
        """Called when the user clicks the mic on the UI."""
        if self.worker is not None and self.worker.isRunning():
            return # Already running
            
        self.worker = VoiceWorker()
        self._connect_worker()
        self.worker.start()

    def handle_text_query(self, text):
        """Called when a user clicks a clarification option."""
        if self.worker is not None and self.worker.isRunning():
            return
            
        # We subclass or create a mock worker that skips listening and uses the text directly
        class TextWorker(VoiceWorker):
            def __init__(self, text_query):
                super().__init__()
                self.text_query = text_query
            def run(self):
                self.processing_started.emit(self.text_query)
                response_data = self.gov_service.process_query(self.text_query)
                if response_data["type"] == "CLARIFICATION":
                    self.clarification_needed.emit(self.text_query, response_data["options"])
                    prompt = "మీకు ఈ పథకాలలో ఏది కావాలి? " + " లేదా ".join(response_data["options"])
                    self.tts_service.speak(prompt)
                else:
                    source = response_data.get("source", {})
                    self.response_ready.emit(self.text_query, response_data["text"], source)
                    self.tts_service.speak(response_data["text"])
                    self.playback_finished.emit()

        self.worker = TextWorker(text)
        self._connect_worker()
        self.worker.start()

    def _connect_worker(self):
        self.worker.listening_started.connect(self.transition_to_listening)
        self.worker.processing_started.connect(self.transition_to_processing)
        self.worker.response_ready.connect(self.transition_to_response)
        self.worker.clarification_needed.connect(self.transition_to_clarification)
        self.worker.error_occurred.connect(self._handle_error)
        
        from PyQt6.QtCore import QTimer
        self.worker.playback_finished.connect(lambda: QTimer.singleShot(50, self.handle_mic_clicked))

    def handle_replay_audio(self, response_text):
        """Called to replay the response audio."""
        # Simple fire and forget in a separate thread so UI doesn't block
        import threading
        threading.Thread(target=self.tts_service.speak, args=(response_text,), daemon=True).start()
        
    def _handle_error(self, error_msg):
        self.show_error.emit(error_msg)
        self.transition_to_home.emit()
