"""Home / kiosk screen: header, mic, 4 quick-access cards, recent questions, status bar."""
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QFrame, QPushButton, QScrollArea, QSizePolicy)
from widgets.components import MicButton, QuickAccessCard, StatusPill
from theme import ACCENT, ACCENT_HI, TEXT, TEXT_MUTED, PANEL, PANEL_HI, BORDER, SUCCESS


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

        press = QLabel("Ask Your Question")
        press.setAlignment(Qt.AlignmentFlag.AlignCenter)
        press.setStyleSheet(f"color: {TEXT}; font-size: 26px; font-weight: 700;")
        center.addWidget(press)

        telugu = QLabel("మీ ప్రశ్న అడగండి")
        telugu.setAlignment(Qt.AlignmentFlag.AlignCenter)
        telugu.setStyleSheet(f"color: {ACCENT_HI}; font-size: 18px; font-weight: 500;")
        center.addWidget(telugu)

        sub = QLabel("Tap the microphone and speak  •  Telugu supported")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 14px;")
        center.addWidget(sub)
        hero = QFrame(); hero.setObjectName("Glass")
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(24, 18, 24, 22)
        hero_layout.addLayout(center)
        root.addWidget(hero)

        # ----- Quick access cards
        cards_title = QLabel("Quick Access")
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
        recent_title = QLabel("Recent Questions")
        recent_title.setStyleSheet(f"color: {TEXT}; font-size: 18px; font-weight: 700; margin-top: 10px;")
        root.addWidget(recent_title)

        recent_box = QFrame(); recent_box.setObjectName("Glass")
        rv = QVBoxLayout(recent_box); rv.setContentsMargins(18,18,18,18); rv.setSpacing(12)
        
        from backend.repositories.query_log_repository import QueryLogRepository
        repo = QueryLogRepository()
        recent_queries = repo.get_recent_queries(limit=3)
        
        if not recent_queries:
            rv.addWidget(self._recent_row("No recent questions available yet."))
        else:
            for q in recent_queries:
                rv.addWidget(self._recent_row(q['query_text'], q))
        root.addWidget(recent_box)

        # ----- Bottom status bar
        status = QHBoxLayout(); status.setSpacing(10)
        for txt, ok in [("AI Ready", True), ("Internet Connected", True),
                        ("Microphone OK", True), ("System Healthy", True)]:
            status.addWidget(StatusPill(txt, ok))
        status.addStretch(1)
        version = QLabel("v1.0 • Public Kiosk")
        version.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
        status.addWidget(version)
        root.addLayout(status)

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
