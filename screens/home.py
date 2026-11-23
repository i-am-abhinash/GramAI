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
from widgets.components import MicButton
from theme import TEXT, TEXT_MUTED, ACCENT, ACCENT_HI


class FloatingGlassBackdrop(QWidget):
    """Design 2: restrained midnight gradient and abstract frosted glass panels."""
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        if w < 1 or h < 1:
            return
        background = QLinearGradient(0, 0, w, h)
        background.setColorAt(0.0, QColor("#030B19"))
        background.setColorAt(.48, QColor("#09142E"))
        background.setColorAt(1.0, QColor("#140F32"))
        p.fillRect(self.rect(), background)
        p.setPen(Qt.PenStyle.NoPen)
        for x, y, radius, color in [
            (.10, .24, .37, QColor(0, 155, 255, 55)),
            (.86, .68, .39, QColor(153, 49, 239, 50)),
            (.50, .91, .32, QColor(0, 189, 240, 28)),
        ]:
            r = min(w, h) * radius
            grad = QRadialGradient(QPointF(w*x, h*y), r)
            grad.setColorAt(0, color)
            grad.setColorAt(1, QColor(0, 0, 0, 0))
            p.setBrush(grad)
            p.drawEllipse(QPointF(w*x, h*y), r, r)
        # Luminous orbital arc without distracting empty cards.
        p.setBrush(Qt.BrushStyle.NoBrush)
        arc = QRectF(w*.08, h*.05, w*.84, h*1.1)
        for j in range(6, 0, -1):
            p.setPen(QPen(QColor(40, 159, 245, 12+j*5), j*1.5))
            p.drawArc(arc, 20*16, 150*16)
        p.setPen(QPen(QColor("#31CEFF"), 2.2))
        p.drawArc(arc, 40*16, 125*16)
        p.setPen(QPen(QColor("#AD55FF"), 2.2))
        p.drawArc(arc, 14*16, 36*16)


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
            QWidget#GramHome { background: #070F22; }
            QFrame#HomeSidebar { background: #0B1930; border-right: 1px solid #203553; }
            QPushButton#HomeNav { background: transparent; color: #D6E5F5;
                text-align: left; border: none; border-radius: 10px;
                padding: 12px 16px; font-size: 14px; font-weight: 600; }
            QPushButton#HomeNav:hover { background: #1B345A; }
            QPushButton#HomeNav:checked { background: #1468C6; color: white; }
            QFrame#QuestionBar { background: rgba(12,28,56,0.91);
                border: 1px solid #3965A1; border-radius: 24px; }
            QLineEdit#QuestionInput { background: transparent; border: none;
                color: white; font-size: 15px; padding: 10px; }
            QPushButton#SendButton { background: #237AF0; color: white;
                border: none; border-radius: 20px; font-size: 19px; font-weight: bold; }
            QPushButton#SendButton:hover { background: #4496FF; }
            QPushButton#LanguagePill { background: #203452; color: #E7F1FF;
                border: 1px solid #3B547A; border-radius: 13px;
                padding: 6px 12px; font-size: 12px; }
            QPushButton#LanguagePill:checked { background: #2763AD; }
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
            button = QPushButton(title)
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
        scene_layout.setContentsMargins(34, 22, 34, 25)
        scene_layout.setSpacing(8)
        body.addWidget(self.scene, 1)

        top = QHBoxLayout()
        menu = QPushButton("☰")
        menu.setToolTip("Open or close navigation")
        menu.setFixedSize(56, 48)
        menu.setCursor(Qt.CursorShape.PointingHandCursor)
        menu.setStyleSheet("QPushButton { background: rgba(8, 32, 59, 0.80); color: #83F0FF; border: 1px solid #27C9F1; border-radius: 14px; font-size: 25px; padding: 0; } QPushButton:hover { background: #15577E; }")
        menu.clicked.connect(self.toggle_sidebar)
        top.addWidget(menu)
        brand = QLabel("✦  Gram<span style='color:#39E4F4'>AI</span>")
        brand.setTextFormat(Qt.TextFormat.RichText)
        brand.setStyleSheet("color: white; font-size: 25px; font-weight: 800;")
        top.addWidget(brand)
        top.addStretch()
        self.telugu = QPushButton("తెలుగు")
        self.english = QPushButton("English")
        for b in (self.telugu, self.english):
            b.setObjectName("LanguagePill")
            b.setCheckable(True)
            top.addWidget(b)
        self.telugu.setChecked(True)
        self.telugu.clicked.connect(lambda: self._set_language(True))
        self.english.clicked.connect(lambda: self._set_language(False))
        scene_layout.addLayout(top)
        scene_layout.addStretch(1)

        title = QLabel("Gram<span style='color:#34D8FF'>A</span><span style='color:#A764FF'>I</span>")
        title.setTextFormat(Qt.TextFormat.RichText)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 70px; font-weight: 800; color: white;")
        scene_layout.addWidget(title)
        subtitle = QLabel("AI Powered Rural Assistance System\n\nYour AI assistant for government schemes, pensions, scholarships,\nration cards, healthcare, housing and more...")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("font-size: 14px; color: #E2EBFA; line-height: 1.4;")
        scene_layout.addWidget(subtitle)
        scene_layout.addSpacing(15)

        center = QHBoxLayout()
        center.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_wave = Waveform()
        right_wave = Waveform()
        self.mic = MicButton(diameter=218)
        self.mic.clicked.connect(self.listen_requested.emit)
        center.addWidget(left_wave)
        center.addWidget(self.mic)
        center.addWidget(right_wave)
        scene_layout.addLayout(center)
        tap = QLabel("Tap and Speak")
        tap.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tap.setStyleSheet("font-size: 18px; font-weight: 700; color: white;")
        scene_layout.addWidget(tap)
        scene_layout.addStretch(1)

        composer = QFrame()
        composer.setObjectName("QuestionBar")
        composer.setMinimumWidth(600)
        composer.setMaximumWidth(830)
        bar = QHBoxLayout(composer)
        bar.setContentsMargins(12, 8, 10, 8)
        bar.setSpacing(7)
        icon = QLabel("☏")
        icon.setStyleSheet("font-size: 22px; color: #A6D8FF;")
        bar.addWidget(icon)
        self.question_input = QLineEdit()
        self.question_input.setObjectName("QuestionInput")
        self.question_input.setPlaceholderText("Ask your question... / మీ ప్రశ్నను అడగండి...")
        self.question_input.setReadOnly(False)
        self.question_input.setToolTip("Type a question and press Enter, or tap the microphone to speak.")
        self.question_input.returnPressed.connect(self._send_question)
        bar.addWidget(self.question_input, 1)
        send = QPushButton("➤")
        send.setObjectName("SendButton")
        send.setFixedSize(40, 40)
        send.clicked.connect(self._send_question)
        bar.addWidget(send)
        scene_layout.addWidget(composer, alignment=Qt.AlignmentFlag.AlignHCenter)

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
