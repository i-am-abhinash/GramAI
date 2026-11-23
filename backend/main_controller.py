from PyQt6.QtCore import QObject, pyqtSignal, QThread
from backend.speech.speech_recognition_service import SpeechRecognitionService
from backend.speech.text_to_speech_service import TextToSpeechService
from backend.services.government_information_service import GovernmentInformationService
from backend.services.feedback_service import FeedbackService

class BaseWorker(QThread):
    listening_started = pyqtSignal()
    processing_started = pyqtSignal(str)
    response_ready = pyqtSignal(str, str, dict)
    clarification_needed = pyqtSignal(str, list)
    error_occurred = pyqtSignal(str)
    playback_finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._is_cancelled = False
        self.gov_service = GovernmentInformationService()
        self.tts_service = TextToSpeechService()

    def stop(self):
        self._is_cancelled = True
        self.tts_service.stop()

    def _process_and_speak(self, text):
        if self._is_cancelled: return
        self.processing_started.emit(text)
        
        response_data = self.gov_service.process_query(text)
        if self._is_cancelled: return
        
        if response_data["type"] == "CLARIFICATION":
            self.clarification_needed.emit(text, response_data["options"])
            prompt = "మీకు ఈ పథకాలలో ఏది కావాలి? " + " లేదా ".join(response_data["options"])
            self.tts_service.speak(prompt)
        else:
            answer_text = response_data["text"]
            source = response_data.get("source", {})
            self.response_ready.emit(text, answer_text, source)
            self.tts_service.speak(answer_text)
            if not self._is_cancelled:
                self.playback_finished.emit()

class VoiceWorker(BaseWorker):
    def __init__(self):
        super().__init__()
        self.speech_service = SpeechRecognitionService()
        
    def run(self):
        self.listening_started.emit()
        result = self.speech_service.listen_and_transcribe()
        if self._is_cancelled: return
        
        if not result["success"]:
            self.error_occurred.emit(result["error"])
            return
            
        self._process_and_speak(result["text"])

class TextWorker(BaseWorker):
    def __init__(self, text):
        super().__init__()
        self.text = text
        
    def run(self):
        self._process_and_speak(self.text)

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
    playback_finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.worker = None
        self.tts_service = TextToSpeechService() # For replay functionality
        self.feedback_service = FeedbackService()
        self._retry_after_silence = False

    def handle_feedback(self, query, response, is_helpful):
        self.feedback_service.record_feedback(query, response, is_helpful)

    def _cancel_active(self):
        """Cancel any running thread and TTS."""
        self.tts_service.stop()
        if self.worker is not None:
            self.worker.stop()
            self.worker.wait() # Wait for it to gracefully exit
            self.worker = None

    def handle_home_clicked(self):
        """Called when user explicitly goes home/cancels."""
        self._cancel_active()
        self.transition_to_home.emit()

    def handle_mic_clicked(self):
        """Called when the user clicks the mic on the UI."""
        self._cancel_active()
        self._retry_after_silence = False
        self.worker = VoiceWorker()
        self._connect_worker()
        self.worker.start()

    def handle_text_query(self, text):
        """Called when a user clicks a clarification option."""
        self._cancel_active()
        self.worker = TextWorker(text)
        self._connect_worker()
        self.worker.start()

    def _connect_worker(self):
        self.worker.listening_started.connect(self.transition_to_listening)
        self.worker.processing_started.connect(self.transition_to_processing)
        self.worker.response_ready.connect(self.transition_to_response)
        self.worker.clarification_needed.connect(self.transition_to_clarification)
        self.worker.error_occurred.connect(self._handle_error)
        self.worker.finished.connect(self._on_worker_finished)
        self.worker.playback_finished.connect(self.playback_finished.emit)

    def handle_replay_audio(self, response_text):
        """Called to replay the response audio."""
        # Simple fire and forget in a separate thread so UI doesn't block
        import threading
        threading.Thread(target=self.tts_service.speak, args=(response_text,), daemon=True).start()
        
    def _handle_error(self, error_msg):
        if error_msg == "Listening timed out. No speech detected.":
            # The listening page remains visible; retry after the worker exits.
            self._retry_after_silence = True
            self.transition_to_listening.emit()
            return
        self.show_error.emit(error_msg)
        self.transition_to_home.emit()

    def _on_worker_finished(self):
        if self._retry_after_silence:
            self._retry_after_silence = False
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(150, self.handle_mic_clicked)
