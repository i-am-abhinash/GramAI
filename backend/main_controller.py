from PyQt6.QtCore import QObject, pyqtSignal, QThread, QTimer
from backend.speech.speech_recognition_service import SpeechRecognitionService
from backend.speech.text_to_speech_service import TextToSpeechService
from backend.services.government_information_service import GovernmentInformationService
from backend.services.feedback_service import FeedbackService
from backend.services.conversation_service import ConversationSession

class BaseWorker(QThread):
    listening_started = pyqtSignal()
    processing_started = pyqtSignal(str)
    response_ready = pyqtSignal(str, str, dict)
    clarification_needed = pyqtSignal(str, list)
    error_occurred = pyqtSignal(str)
    playback_finished = pyqtSignal()
    conversation_ended = pyqtSignal()

    def __init__(self, language='te', session=None):
        super().__init__()
        self.language = language
        self.session = session if session is not None else ConversationSession()
        self._is_cancelled = False
        self.gov_service = GovernmentInformationService()
        self.tts_service = TextToSpeechService()

    def stop(self):
        self._is_cancelled = True
        self.tts_service.stop()

    def _process_and_speak(self, text):
        if self._is_cancelled: return
        self.processing_started.emit(text)
        
        response_data = self.session.process(self.gov_service, text, language=self.language)
        if self._is_cancelled: return
        
        if response_data["type"] == "END":
            self.conversation_ended.emit()
            return
        if response_data["type"] == "CLARIFICATION":
            self.clarification_needed.emit(text, response_data["options"])
            prompt = (("Which of these schemes do you mean? " + " or ".join(response_data["options"])) if self.language == "en" else ("మీకు ఈ పథకాలలో ఏది కావాలి? " + " లేదా ".join(response_data["options"])))
            self.tts_service.speak(prompt, language=self.language)
            if not self._is_cancelled:
                self.playback_finished.emit()
        else:
            answer_text = response_data["text"]
            source = response_data.get("source", {})
            self.response_ready.emit(text, answer_text, source)
            self.tts_service.speak(answer_text, language=self.language)
            if not self._is_cancelled:
                self.playback_finished.emit()

class VoiceWorker(BaseWorker):
    def __init__(self, language='te', session=None, timeout=15):
        super().__init__(language=language, session=session)
        self.timeout = timeout
        self.speech_service = SpeechRecognitionService()
        
    def run(self):
        self.listening_started.emit()
        lang_code = 'en-IN' if self.language == 'en' else 'te-IN'
        result = self.speech_service.listen_and_transcribe(language=lang_code, timeout=self.timeout)
        if self._is_cancelled: return
        
        if not result["success"]:
            self.error_occurred.emit(result["error"])
            return
            
        self._process_and_speak(result["text"])

class TextWorker(BaseWorker):
    def __init__(self, text, language='te', session=None):
        super().__init__(language=language, session=session)
        self.text = text
        
    def run(self):
        self._process_and_speak(self.text)

class PromptWorker(BaseWorker):
    def __init__(self, text, language, session, show_prompt=True):
        super().__init__(language=language, session=session)
        self.text = text
        self.show_prompt = show_prompt

    def run(self):
        if self._is_cancelled:
            return
        if self.show_prompt:
            self.response_ready.emit("", self.text, {})
        self.tts_service.speak(self.text, language=self.language)
        if not self._is_cancelled:
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
    playback_finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.worker = None
        self.tts_service = TextToSpeechService() # For replay functionality
        self.feedback_service = FeedbackService()
        self.session = ConversationSession()
        self.session_active = False
        self._silence_count = 0
        self._after_worker = None
        self.language = "te"

    def set_language(self, language):
        new_language = "en" if str(language).lower().startswith("en") else "te"
        if new_language != self.language:
            self.language = new_language
            self.session = ConversationSession()
            if self.session_active:
                self.start_voice_session()

    def handle_feedback(self, query, response, is_helpful):
        self.feedback_service.record_feedback(query, response, is_helpful)

    def _cancel_active(self):
        """Cancel old work before starting another microphone or playback."""
        self._after_worker = None
        self.tts_service.stop()
        if self.worker is not None:
            worker = self.worker
            self.worker = None
            worker.stop()
            worker.wait()
            worker.deleteLater()

    def reset_session(self):
        self.session_active = False
        self._cancel_active()
        self.session = ConversationSession()
        self._silence_count = 0

    def handle_home_clicked(self):
        self.reset_session()
        self.transition_to_home.emit()

    def start_voice_session(self):
        self.reset_session()
        self.session_active = True
        self.handle_mic_clicked()

    def start_text_session(self, text):
        self.reset_session()
        self.session_active = True
        self.handle_text_query(text)

    def handle_mic_clicked(self):
        self._cancel_active()
        if not self.session_active:
            self.session = ConversationSession()
            self.session_active = True
        self.worker = VoiceWorker(language=self.language, session=self.session,
                                  timeout=10 if self._silence_count else 15)
        self._connect_worker()
        self.worker.start()

    def handle_text_query(self, text):
        self._cancel_active()
        self.session_active = True
        self._silence_count = 0
        self.worker = TextWorker(text, language=self.language, session=self.session)
        self._connect_worker()
        self.worker.start()

    def _connect_worker(self):
        self.worker.listening_started.connect(self._listening)
        self.worker.processing_started.connect(self._processing)
        self.worker.response_ready.connect(self._response)
        self.worker.clarification_needed.connect(self._clarification)
        self.worker.error_occurred.connect(self._handle_error)
        self.worker.finished.connect(self._on_worker_finished)
        self.worker.playback_finished.connect(self._playback_finished)
        self.worker.conversation_ended.connect(self._end_conversation)

    def _current(self):
        return self.worker is not None and self.sender() is self.worker and self.session_active

    def _listening(self):
        if self._current():
            self.transition_to_listening.emit()

    def _processing(self, text):
        if self._current():
            self._silence_count = 0
            self.transition_to_processing.emit(text)

    def _response(self, question, answer, source):
        if self._current():
            self.transition_to_response.emit(question, answer, source)

    def _clarification(self, question, options):
        if self._current():
            self.transition_to_clarification.emit(question, options)

    def _playback_finished(self):
        if self._current():
            self.playback_finished.emit()

    def _end_conversation(self):
        if self._current():
            self.handle_home_clicked()

    def handle_replay_audio(self, response_text):
        self._cancel_active()
        if self.session_active:
            self.worker = PromptWorker(response_text, self.language, self.session, show_prompt=False)
            self._connect_worker()
            self.worker.start()

    def _handle_error(self, error_msg):
        if not self._current():
            return
        if error_msg in ("Listening timed out. No speech detected.", "Sorry, I could not understand the audio."):
            if self._silence_count == 0:
                self._silence_count = 1
                self._after_worker = "reminder"
            else:
                self._after_worker = "home"
            return
        self.show_error.emit(error_msg)
        self._after_worker = "home"

    def _on_worker_finished(self):
        if not self._current():
            return
        worker = self.worker
        self.worker = None
        worker.deleteLater()
        action = self._after_worker
        self._after_worker = None
        if action == "home":
            self.handle_home_clicked()
        elif action == "reminder":
            prompt = "Do you have another question?" if self.language == "en" else "ఇంకేమైనా అడగాలనుకుంటున్నారా?"
            self.worker = PromptWorker(prompt, self.language, self.session)
            self._connect_worker()
            self.worker.start()
