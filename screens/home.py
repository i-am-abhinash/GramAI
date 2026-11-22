"""Home / kiosk screen: header, mic, 4 quick-access cards, recent questions, status bar."""
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QFrame, QPushButton, QScrollArea, QSizePolicy)
from widgets.components import MicButton, QuickAccessCard, StatusPill
from theme import ACCENT, ACCENT_HI, TEXT, TEXT_MUTED, PANEL, PANEL_HI, BORDER, SUCCESS
from backend.locale.i18n import I18n
from backend.repositories.query_log_repository import QueryLogRepository

class HomeScreen(QWidget):
    listen_requested = pyqtSignal()
    card_clicked     = pyqtSignal(str)
    recent_clicked   = pyqtSignal(str, str, dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        root = QVBoxLayout(container); root.setContentsMargins(48, 32, 48, 24); root.setSpacing(22)

        # ----- Center: mic + label
        center = QVBoxLayout(); center.setAlignment(Qt.AlignmentFlag.AlignHCenter); center.setSpacing(8)
        self.mic = MicButton(diameter=208)
        self.mic.clicked.connect(self.listen_requested.emit)
        center.addWidget(self.mic, alignment=Qt.AlignmentFlag.AlignHCenter)

        press = QLabel(I18n.get("home_ask"))
        press.setAlignment(Qt.AlignmentFlag.AlignCenter)
        press.setStyleSheet(f"color: {TEXT}; font-size: 26px; font-weight: 700;")
        center.addWidget(press)

        telugu = QLabel(I18n.get("home_telugu"))
        telugu.setAlignment(Qt.AlignmentFlag.AlignCenter)
        telugu.setStyleSheet(f"color: {ACCENT_HI}; font-size: 18px; font-weight: 500;")
        center.addWidget(telugu)

        sub = QLabel(I18n.get("home_hint"))
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 14px;")
        center.addWidget(sub)
        hero = QFrame(); hero.setObjectName("Glass")
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(24, 18, 24, 22)
        hero_layout.addLayout(center)
        root.addWidget(hero)

        # ----- Quick access cards
        cards_title = QLabel(I18n.get("home_quick"))
        cards_title.setStyleSheet(f"color: {TEXT}; font-size: 18px; font-weight: 700; margin-top: 6px;")
        root.addWidget(cards_title)

        grid = QGridLayout(); grid.setSpacing(16)
        cards = [
            ("Government Schemes", "Browse welfare programs", "📄", "schemes"),
            ("Pension Services",   "Old age & widow pension", "👵", "pension"),
            ("Ration Card",        "Status & corrections",    "🪪", "ration"),
            ("Scholarships",       "Student aid information", "🎓", "scholar"),
        ]
        for i, (t, s, e, k) in enumerate(cards):
            c = QuickAccessCard(t, s, e, k)
            c.clicked.connect(self.card_clicked.emit)
            grid.addWidget(c, 0, i)
        root.addLayout(grid)

        # ----- Recent questions panel
        recent_title = QLabel(I18n.get("home_recent"))
        recent_title.setStyleSheet(f"color: {TEXT}; font-size: 18px; font-weight: 700; margin-top: 10px;")
        root.addWidget(recent_title)

        recent_box = QFrame(); recent_box.setObjectName("Glass")
        rv = QVBoxLayout(recent_box); rv.setContentsMargins(18,18,18,18); rv.setSpacing(12)
        
        repo = QueryLogRepository()
        recent_queries = repo.get_recent_queries(limit=3)
        
        if not recent_queries:
            rv.addWidget(self._recent_row(I18n.get("no_recent_questions")))
        else:
            for q in recent_queries:
                rv.addWidget(self._recent_row(q['query_text'], q))
        root.addWidget(recent_box)

        # ----- Bottom status bar
        status = QHBoxLayout(); status.setSpacing(10)
        
        self.pill_ai = StatusPill("AI Ready", False)
        self.pill_net = StatusPill("Internet Connected", False)
        self.pill_mic = StatusPill("Microphone OK", False)
        self.pill_sys = StatusPill("System Healthy", False)
        
        status.addWidget(self.pill_ai)
        status.addWidget(self.pill_net)
        status.addWidget(self.pill_mic)
        status.addWidget(self.pill_sys)
        
        status.addStretch(1)
        version = QLabel("v1.0 • Public Kiosk")
        version.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
        status.addWidget(version)
        root.addLayout(status)
        
        from PyQt6.QtCore import QTimer
        self._health_timer = QTimer(self)
        self._health_timer.timeout.connect(self.check_health)
        self._health_timer.start(15000) # Check every 15s
        
        # Run initial check after a small delay
        QTimer.singleShot(500, self.check_health)

    def check_health(self):
        import urllib.request
        import speech_recognition as sr
        from backend.database.mysql_connection import db
        
        # Check DB
        db_ok = False
        try:
            conn = db.connect()
            if conn:
                db_ok = True
                conn.close()
        except Exception:
            pass
            
        # Check Internet
        net_ok = False
        try:
            urllib.request.urlopen('http://8.8.8.8', timeout=1)
            net_ok = True
        except Exception:
            pass
            
        # Check Mic
        mic_ok = False
        try:
            mics = sr.Microphone.list_microphone_names()
            if mics and len(mics) > 0:
                mic_ok = True
        except Exception:
            pass
            
        self.pill_ai.set_status(db_ok and net_ok)
        self.pill_net.set_status(net_ok)
        self.pill_mic.set_status(mic_ok)
        self.pill_sys.set_status(db_ok)

    def _recent_row(self, text: str, data: dict = None) -> QFrame:
        row = QFrame(); row.setObjectName("Card")
        row.setStyleSheet(f"QFrame#Card {{background:{PANEL_HI}; border:1px solid {BORDER}; border-radius:12px;}}")
        h = QHBoxLayout(row); h.setContentsMargins(14,10,10,10); h.setSpacing(10)
        lbl = QLabel(text); lbl.setStyleSheet(f"color:{TEXT}; font-size: 15px;")
        h.addWidget(lbl, 1)
        play = QPushButton("▶ Open"); play.setObjectName("Primary")
        play.setStyleSheet("padding: 8px 16px; font-size: 14px;")
        
        if data:
            source_dict = {"name": data.get("response_source", "Unknown"), "url": "", "date": ""}
            play.clicked.connect(lambda _, d=data, s=source_dict: self.recent_clicked.emit(d['query_text'], d['response_text'], s))
        else:
            play.hide()
            
        h.addWidget(play)
        return row
