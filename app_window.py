"""Main window — owns a QStackedWidget that swaps screens (kiosk + admin)."""
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStackedWidget

from widgets.header     import HeaderBar
from screens.home       import HomeScreen
from screens.listening  import ListeningScreen
from screens.processing import ProcessingScreen
from screens.response   import ResponseScreen
from screens.clarification import ClarificationScreen
from screens.admin_login import AdminLoginScreen
from admin.shell        import AdminShell


from backend.main_controller import MainController

class MainWindow(QMainWindow):
    # stack indices
    HOME, LISTEN, PROCESS, RESPONSE, CLARIFICATION, ADMIN_LOGIN, ADMIN = range(7)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("GramAI — AI Powered Rural Assistance System")
        self.setMinimumSize(1200, 780)

        # Initialize Main Controller
        self.controller = MainController()

        central = QWidget(); self.setCentralWidget(central)
        v = QVBoxLayout(central); v.setContentsMargins(0,0,0,0); v.setSpacing(0)

        self.header = HeaderBar()
        self.header.admin_clicked.connect(self._show_admin_login)
        v.addWidget(self.header)

        self.stack = QStackedWidget()
        v.addWidget(self.stack, 1)

        # Screens
        self.home       = HomeScreen()
        self.listening  = ListeningScreen()
        self.processing = ProcessingScreen()
        self.response   = ResponseScreen()
        self.clarification = ClarificationScreen()
        self.admin_login = AdminLoginScreen()
        self.admin      = AdminShell()

        for w in (self.home, self.listening, self.processing,
                  self.response, self.clarification, self.admin_login, self.admin):
            self.stack.addWidget(w)

        self.header.hide()  # The redesigned home has its own full-height sidebar.

        # Wire UI actions to controller
        self.home.language_changed.connect(self._set_language)
        self.listening.language_changed.connect(self._set_language)
        self.home.listen_requested.connect(self.controller.handle_mic_clicked)
        self.home.text_requested.connect(self.controller.handle_text_query)
        self.home.card_clicked.connect(lambda _key: self.controller.handle_mic_clicked())
        self.home.recent_clicked.connect(self._show_response)
        self.home.admin_requested.connect(self._show_admin_login)
        
        self.response.ask_again.connect(self.controller.handle_mic_clicked)
        self.response.replay_audio.connect(self.controller.handle_replay_audio)
        self.response.submit_feedback.connect(self.controller.handle_feedback)
        
        # Wire Clarification UI to controller
        self.clarification.cancelled.connect(self._show_home)
        self.clarification.option_selected.connect(self.controller.handle_text_query)
        
        # Wire UI internal navigation
        self.listening.cancelled.connect(self._show_home)
        self.listening.home_requested.connect(self._show_home)
        self.response.return_home.connect(self._show_home)
        self.admin_login.back.connect(self._show_home)
        self.admin_login.login_ok.connect(self._show_home_admin)
        self.admin.logout.connect(self._logout_admin)

        # Wire Controller actions to UI
        self.controller.transition_to_listening.connect(self._show_listening)
        self.controller.transition_to_processing.connect(self._show_processing)
        self.controller.transition_to_response.connect(self._show_response)
        self.controller.transition_to_clarification.connect(self._show_clarification)
        self.controller.transition_to_home.connect(self._show_home)

    def _set_language(self, language):
        self.controller.set_language(language)
        if self.listening.telugu.isChecked() != (language == 'te'):
            self.listening.set_language(language)
        self.response.set_language(language)

    def _logout_admin(self):
        """End the authenticated admin session and return to the public home."""
        from backend.services.auth_service import AuthService
        AuthService.logout()
        self.admin.sidebar.hide()
        self._show_home()

    def _show_admin_login(self):
        self.header.hide()
        self.stack.setCurrentIndex(self.ADMIN_LOGIN)

    def _show_home_admin(self):
        self._enter_admin()

    def _show_home(self):
        # Dynamically refresh the home screen to fetch new recent FAQs
        old_home = self.stack.widget(self.HOME)
        self.stack.removeWidget(old_home)
        old_home.deleteLater()
        
        self.home = HomeScreen()
        self.home.language_changed.connect(self._set_language)
        self.home._set_language(self.controller.language == 'te')
        self.home.listen_requested.connect(self.controller.handle_mic_clicked)
        self.home.text_requested.connect(self.controller.handle_text_query)
        self.home.card_clicked.connect(lambda _key: self.controller.handle_mic_clicked())
        self.home.recent_clicked.connect(self._show_response)
        self.home.admin_requested.connect(self._show_admin_login)
        
        self.stack.insertWidget(self.HOME, self.home)
        self.header.hide()
        self.stack.setCurrentIndex(self.HOME)

    def _show_listening(self):
        self.header.hide()
        if self.listening.telugu.isChecked() != (self.controller.language == 'te'):
            self.listening.set_language(self.controller.language)
        self.stack.setCurrentIndex(self.LISTEN)

    def _show_processing(self, recognized_text):
        # We could display the recognized text on the processing screen here
        self.header.show()
        self.stack.setCurrentIndex(self.PROCESS)

    def _show_response(self, question, answer, source):
        self.response.set_data(question, answer, source)
        self.header.hide()
        self.stack.setCurrentIndex(self.RESPONSE)
        
    def _show_clarification(self, question, options):
        self.clarification.set_options(options)
        self.header.show()
        self.stack.setCurrentIndex(self.CLARIFICATION)

    def _enter_admin(self):
        # Hide kiosk header — admin shell has its own sidebar branding
        self.header.hide()
        # Force refresh of the active admin tab so live data is shown immediately on login
        self.admin._switch_tab(self.admin.stack.currentIndex())
        self.stack.setCurrentIndex(self.ADMIN)
