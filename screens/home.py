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


class VillageBackdrop(QWidget):
    """Lightweight vector sunset scene; no external image or network dependency."""
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        if not w or not h:
            return
        sky = QLinearGradient(0, 0, w, h)
        sky.setColorAt(0, QColor("#020A18"))
        sky.setColorAt(.42, QColor("#071C3B"))
        sky.setColorAt(.78, QColor("#172354"))
        sky.setColorAt(1, QColor("#39285C"))
        p.fillRect(self.rect(), sky)
        # Moonlit rural scene and subtle star field.
        p.setPen(Qt.PenStyle.NoPen)
        for i in range(38):
            sx = (i * 151 + 47) % max(1, int(w))
            sy = (i * 73 + 29) % max(1, int(h * .55))
            p.setBrush(QColor(157, 219, 255, 65 + i % 4 * 32))
            p.drawEllipse(QPointF(sx, sy), 0.7 + i % 3 * .35, 0.7 + i % 3 * .35)
        mx, my = w*.85, h*.23
        glow = QRadialGradient(QPointF(mx, my), h*.115)
        glow.setColorAt(0, QColor(138, 207, 255, 95))
        glow.setColorAt(1, QColor(40, 90, 170, 0))
        p.setBrush(glow)
        p.drawEllipse(QPointF(mx, my), h*.115, h*.115)
        p.setBrush(QColor("#C4E6FF"))
        p.drawEllipse(QPointF(mx, my), h*.026, h*.026)
        horizon = h * .72
        sun = QRadialGradient(QPointF(w*.84, horizon), h*.22)
        sun.setColorAt(0, QColor(255, 189, 126, 200))
        sun.setColorAt(1, QColor(255, 150, 110, 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(sun)
        p.drawEllipse(QPointF(w*.84, horizon), h*.22, h*.22)
        for y, color, height in [
            (h*.78, "#152F4A", h*.10),
            (h*.85, "#173F42", h*.11),
            (h*.91, "#184D42", h*.10),
        ]:
            path = QPainterPath()
            path.moveTo(0, h)
            path.lineTo(0, y)
            path.cubicTo(w*.25, y-height, w*.54, y+height, w, y-height*.45)
            path.lineTo(w, h)
            path.closeSubpath()
            p.fillPath(path, QColor(color))
        # Small village buildings, kept behind the UI.
        for x, size in [(0.13, .060), (.22, .042), (.75, .045), (.87, .052)]:
            bw = w*size
            bh = h*.065
            bx, by = w*x, h*.80-bh
            p.fillRect(QRectF(bx, by, bw, bh), QColor("#18334A"))
            roof = QPainterPath()
            roof.moveTo(bx-5, by)
            roof.lineTo(bx+bw*.5, by-bh*.65)
            roof.lineTo(bx+bw+5, by)
            roof.closeSubpath()
            p.fillPath(roof, QColor("#102A40"))
            p.fillRect(QRectF(bx+bw*.48, by+bh*.40, bw*.15, bh*.25), QColor("#E9AD69"))
        # Silhouette windmill.
        x, y = w*.92, h*.78
        p.setPen(QPen(QColor("#132F41"), 3))
        p.drawLine(QPointF(x, y), QPointF(x-12, h*.91))
        p.drawLine(QPointF(x, y), QPointF(x+12, h*.91))
        for angle in range(0, 360, 45):
            a = math.radians(angle)
            p.drawLine(QPointF(x, y), QPointF(x+math.cos(a)*22, y+math.sin(a)*22))


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
            QFrame#QuestionBar { background: rgba(8,25,53,0.88);
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
        logo = QLabel("🌱 Gram<span style='color:#62C7FF'>AI</span>")
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

        self.scene = VillageBackdrop()
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
        brand = QLabel("🌱  Gram<span style='color:#39E4F4'>AI</span>")
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
        scene_layout.addStretch(2)

        title = QLabel("Welcome to <span style='color:#66DEFF'>GramAI</span>")
        title.setTextFormat(Qt.TextFormat.RichText)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 38px; font-weight: 800; color: white;")
        scene_layout.addWidget(title)
        subtitle = QLabel("Ask about government schemes, pensions, scholarships,\nration cards, healthcare, housing and more...")
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
        scene_layout.addStretch(3)

        composer = QFrame()
        composer.setObjectName("QuestionBar")
        composer.setMaximumWidth(690)
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
