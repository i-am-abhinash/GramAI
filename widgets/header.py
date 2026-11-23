"""Top header bar — used by both kiosk and admin shells."""
from PyQt6.QtCore import Qt, QTimer, QTime, pyqtSignal
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget
from theme import ACCENT, ACCENT_HI, TEXT, TEXT_MUTED, PANEL, BORDER, SUCCESS
from widgets.components import GlassButton


class HeaderBar(QFrame):
    admin_clicked = pyqtSignal()
    home_clicked  = pyqtSignal()

    def __init__(self, show_admin: bool = True, parent=None):
        super().__init__(parent)
        self.setObjectName("HeaderBar")
        self.setFixedHeight(78)
        h = QHBoxLayout(self); h.setContentsMargins(30, 9, 30, 9); h.setSpacing(18)

        # Admin login icon (left)
        self.admin_btn = GlassButton("☰")
        self.admin_btn.setObjectName("IconBtn")
        self.admin_btn.setToolTip("Open admin login")
        self.admin_btn.setFixedSize(50,48)
        self.admin_btn.clicked.connect(self.admin_clicked.emit)
        if show_admin:
            h.addWidget(self.admin_btn)

        # Logo bubble
        logo = QLabel("G")
        logo.setFixedSize(46, 46)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 {ACCENT_HI}, stop:1 {ACCENT});
            color: white; font-size: 26px; font-weight: 800;
            border-radius: 23px;
        """)
        h.addWidget(logo)

        # Title block
        title_box = QVBoxLayout(); title_box.setSpacing(2)
        t1 = QLabel("GramAI"); t1.setObjectName("Brand")
        t2 = QLabel("AI Powered Rural Assistance System")
        t2.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 13px; letter-spacing: 0.4px;")
        title_box.addWidget(t1); title_box.addWidget(t2)
        h.addLayout(title_box)
        h.addStretch(1)

        # Right side: time + system status
        right = QHBoxLayout(); right.setSpacing(14)
        self.time_lbl = QLabel(""); self.time_lbl.setStyleSheet(
            f"color: {TEXT}; font-size: 18px; font-weight: 600;"
        )
        right.addWidget(self.time_lbl)

        status = QLabel("●  SYSTEM READY")
        status.setStyleSheet(
            f"color: {SUCCESS}; font-weight: 700; font-size: 13px;"
            f" background: rgba(34,197,94,40); border-radius: 10px; padding: 6px 12px;"
        )
        right.addWidget(status)
        h.addLayout(right)

        self._tick(); t = QTimer(self); t.timeout.connect(self._tick); t.start(1000)

    def _tick(self):
        self.time_lbl.setText(QTime.currentTime().toString("hh:mm AP"))
