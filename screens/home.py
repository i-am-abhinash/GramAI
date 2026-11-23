"""GramAI home screen: screenshot-inspired desktop kiosk interface.

Visual-only redesign. Public signals are retained for MainWindow integration.
"""
import math
from PyQt6.QtCore import Qt, pyqtSignal, QRectF, QPointF
from PyQt6.QtGui import QColor, QPainter, QPen, QLinearGradient, QRadialGradient, QPainterPath
from PyQt6.QtWidgets import (
    QWidget, QFrame, QLabel, QPushButton, QHBoxLayout, QVBoxLayout,
    QLineEdit, QScrollArea, QSizePolicy, QMessageBox
)
from widgets.components import MicButton, GlassButton
from widgets.aurora import AuroraSurface
from theme import TEXT, TEXT_MUTED, ACCENT, ACCENT_HI


class FloatingGlassBackdrop(AuroraSurface):
    pass


class Waveform(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(126, 64)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        mid = self.height()/2
        heights = [5, 12, 22, 10, 32, 47, 23, 13, 37, 20, 9, 17, 6]
        for i, value in enumerate(heights):
            x = 5 + i*9.5
            grad = QLinearGradient(x, mid-value/2, x, mid+value/2)
            grad.setColorAt(0, QColor("#8F9AFF"))
            grad.setColorAt(1, QColor("#71D9FF"))
            p.setPen(QPen(grad, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            p.drawLine(QPointF(x, mid-value/2), QPointF(x, mid+value/2))


class HomeScreen(QWidget):
    listen_requested = pyqtSignal()
    card_clicked = pyqtSignal(str)
    recent_clicked = pyqtSignal(str, str, dict)
    admin_requested = pyqtSignal()
    text_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("GramHome")
        self.setStyleSheet("""
            QWidget#GramHome { background: #020612; }
            QFrame#HomeSidebar { background: #0B1930; border-right: 1px solid #203553; }
            QPushButton#HomeNav { background: transparent; color: #D6E5F5;
                text-align: left; border: none; border-radius: 10px;
                padding: 12px 16px; font-size: 14px; font-weight: 600; }
            QPushButton#HomeNav:hover { background: #1B345A; }
            QPushButton#HomeNav:checked { background: #1468C6; color: white; }
            QFrame#QuestionBar { background: rgba(10,22,47,0.94);
                border: 1px solid #37A7E3; border-radius: 30px; }
            QLineEdit#QuestionInput { background: transparent; border: none;
                color: white; font-size: 18px; padding: 10px; }
            QPushButton#SendButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #08BCEB,stop:.53 #236AEF,stop:1 #B73AFF); color: white;
                border: 1px solid #70DFFF; border-radius: 25px; font-size: 22px; font-weight: bold; }
            QPushButton#SendButton:hover { background: #4496FF; }
            QPushButton#LanguagePill { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #122B4D,stop:1 #1D153C); color: #E7F1FF;
                border: 1px solid #4D79AD; border-radius: 20px;
                padding: 4px 13px; font-size: 13px; }
            QPushButton#LanguagePill:checked { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #006B95,stop:1 #39248C); border: 2px solid #32EAFF; color: white; }
        """)
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        sidebar = QFrame()
        self.sidebar = sidebar
        sidebar.setObjectName("HomeSidebar")
        sidebar.setFixedWidth(230)
        nav = QVBoxLayout(sidebar)
        nav.setContentsMargins(17, 24, 17, 18)
        nav.setSpacing(7)
        logo = QLabel("✦ Gram<span style='color:#62C7FF'>AI</span>")
        logo.setTextFormat(Qt.TextFormat.RichText)
        logo.setStyleSheet("font-size: 27px; font-weight: 800; color: white; padding: 4px 6px 20px;")
        nav.addWidget(logo)
        nav_items = [
            ("⌂    AI Assistant", "assistant"),
            ("▱    Schemes", "schemes"),
            ("◷    My Queries", "queries"),
            ("☆    Feedback", "feedback"),
            ("♙    Admin", "admin"),
            ("⚙    Settings", "settings"),
            ("ⓘ    About", "about"),
        ]
        self.nav_buttons = {}
        for title, key in nav_items:
            button = GlassButton(title)
            button.setObjectName("HomeNav")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setCheckable(True)
            button.clicked.connect(lambda checked=False, k=key: self._navigate(k))
            nav.addWidget(button)
            self.nav_buttons[key] = button
        self.nav_buttons["assistant"].setChecked(True)
        nav.addStretch()
        footer = QLabel("GramAI  •  Rural Assistance")
        footer.setStyleSheet("color: #7990B2; font-size: 11px; padding: 8px;")
        nav.addWidget(footer)
        root.addWidget(sidebar)
        sidebar.hide()  # Design 3: full-width interface until menu is opened.

        main = QFrame()
        main.setStyleSheet("QFrame { background: transparent; }")
        root.addWidget(main, 1)
        body = QVBoxLayout(main)
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        self.scene = FloatingGlassBackdrop()
        scene_layout = QVBoxLayout(self.scene)
        scene_layout.setContentsMargins(34, 18, 34, 24)
        scene_layout.setSpacing(4)
        body.addWidget(self.scene, 1)

        top = QHBoxLayout()
        menu = GlassButton("☰")
        menu.setToolTip("Open or close navigation")
        menu.setFixedSize(48, 46)
        menu.setCursor(Qt.CursorShape.PointingHandCursor)
        menu.setFont(menu.font())
        menu.clicked.connect(self.toggle_sidebar)
        top.addWidget(menu)
        brand = QLabel("Gram<span style='color:#39E4F4'>AI</span>")
        brand.setTextFormat(Qt.TextFormat.RichText)
        brand.setStyleSheet("color: white; font-size: 20px; font-weight: 750;")
        top.addWidget(brand)
        top.addStretch()
        self.telugu = GlassButton("తెలుగు", pill=True)
        self.english = GlassButton("English", pill=True)
        for b in (self.telugu, self.english):
            b.setFixedHeight(40)
            b.setMinimumWidth(84)
            b.setObjectName("LanguagePill")
            b.setCheckable(True)
            top.addWidget(b)
        self.telugu.setChecked(True)
        self.telugu.clicked.connect(lambda: self._set_language(True))
        self.english.clicked.connect(lambda: self._set_language(False))
        scene_layout.addLayout(top)
        scene_layout.addSpacing(2)

        title = QLabel("Gram<span style='color:#34D8FF'>A</span><span style='color:#A764FF'>I</span>")
        title.setTextFormat(Qt.TextFormat.RichText)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-family: Segoe UI Variable; font-size: 65px; font-weight: 800; color: white;")
        scene_layout.addWidget(title)
        subtitle = QLabel("AI Powered Rural Assistance System\nYour AI assistant for government schemes, pensions, scholarships,\nration cards, healthcare, housing and more...")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("font-size: 15px; color: #D7E6FA;")
        scene_layout.addWidget(subtitle)
        scene_layout.addSpacing(5)

        center = QHBoxLayout()
        center.setSpacing(8)
        center.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_wave = Waveform()
        right_wave = Waveform()
        self.mic = MicButton(diameter=178)
        self.mic.clicked.connect(self.listen_requested.emit)
        center.addStretch(1)
        center.addWidget(left_wave)
        center.addWidget(self.mic)
        center.addWidget(right_wave)
        center.addStretch(1)
        scene_layout.addLayout(center)
        tap = QLabel("Tap and Speak")
        tap.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tap.setStyleSheet("font-size: 20px; font-weight: 700; color: white;")
        scene_layout.addWidget(tap)
        scene_layout.addStretch(1)

        composer = QFrame()
        composer.setObjectName("QuestionBar")
        composer.setMinimumWidth(600)
        composer.setMaximumWidth(830)
        bar = QHBoxLayout(composer)
        bar.setContentsMargins(12, 8, 10, 8)
        bar.setSpacing(7)
        icon = QLabel("◉")
        icon.setStyleSheet("font-size: 22px; color: #A6D8FF;")
        bar.addWidget(icon)
        self.question_input = QLineEdit()
        self.question_input.setObjectName("QuestionInput")
        self.question_input.setPlaceholderText("Ask your question... / మీ ప్రశ్నను అడగండి...")
        self.question_input.setReadOnly(False)
        self.question_input.setToolTip("Type a question and press Enter, or tap the microphone to speak.")
        self.question_input.returnPressed.connect(self._send_question)
        bar.addWidget(self.question_input, 1)
        send = GlassButton("➤", pill=True)
        send.setObjectName("SendButton")
        send.setFixedSize(50, 50)
        send.clicked.connect(self._send_question)
        bar.addWidget(send)
        scene_layout.addWidget(composer, alignment=Qt.AlignmentFlag.AlignHCenter)
        scene_layout.addSpacing(6)

    def toggle_sidebar(self):
        self.sidebar.setVisible(not self.sidebar.isVisible())

    def _send_question(self):
        question = self.question_input.text().strip()
        if question:
            self.text_requested.emit(question)
        else:
            self.listen_requested.emit()

    def _set_language(self, telugu):
        self.telugu.setChecked(telugu)
        self.english.setChecked(not telugu)
        # Language choice is visual only; the existing recognition service determines input language.

    def _navigate(self, key):
        if key == "admin":
            self.sidebar.hide()
            self.admin_requested.emit()
            return
        if key == "schemes":
            self.sidebar.hide()
            self.card_clicked.emit("schemes")
            return
        if key == "queries":
            self.sidebar.hide()
            self._show_recent_queries()
            return
        if key == "feedback":
            QMessageBox.information(self, "Feedback", "Ask a question and use the feedback buttons on the answer screen.")
            return
        if key == "settings":
            QMessageBox.information(self, "Settings", "Language and speech settings are managed by the current GramAI configuration.")
            return
        if key == "about":
            QMessageBox.about(self, "About GramAI", "GramAI — AI Powered Rural Assistance System.\nVoice-first access to government information.")
            return
        self.sidebar.hide()
        self.nav_buttons["assistant"].setChecked(True)

    def _show_recent_queries(self):
        try:
            from backend.repositories.query_log_repository import QueryLogRepository
            recent = QueryLogRepository().get_recent_queries(limit=10)
        except Exception as exc:
            QMessageBox.warning(self, "Recent Questions", f"Unable to load recent questions:\n{exc}")
            return
        if not recent:
            QMessageBox.information(self, "Recent Questions", "No recent questions available yet.")
            return
        # Preserve the existing recent_clicked signal contract.
        from PyQt6.QtWidgets import QDialog, QListWidget, QDialogButtonBox
        dialog = QDialog(self)
        dialog.setWindowTitle("Recent Questions")
        dialog.resize(620, 420)
        layout = QVBoxLayout(dialog)
        entries = QListWidget()
        for item in recent:
            entries.addItem(item.get("query_text", "Question"))
        layout.addWidget(entries)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        def open_entry(index):
            item = recent[index.row()]
            source = {"name": item.get("response_source", "Unknown"), "url": "", "date": ""}
            dialog.accept()
            self.recent_clicked.emit(item.get("query_text", ""), item.get("response_text", ""), source)
        entries.doubleClicked.connect(open_entry)
        dialog.exec()
