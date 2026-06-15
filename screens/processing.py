"""AI processing / 'thinking' screen."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from widgets.components import ThinkingSpinner
from theme import TEXT, ACCENT_HI, TEXT_MUTED


class ProcessingScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        v = QVBoxLayout(self); v.setContentsMargins(40,40,40,40); v.setSpacing(20)
        v.addStretch(1)
        sp = ThinkingSpinner(); sp.setFixedSize(220, 220)
        v.addWidget(sp, alignment=Qt.AlignmentFlag.AlignHCenter)

        t = QLabel("Searching Information..."); t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t.setStyleSheet(f"color: {TEXT}; font-size: 28px; font-weight: 700;")
        v.addWidget(t)

        tt = QLabel("సమాచారాన్ని వెతుకుతున్నాను…"); tt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tt.setStyleSheet(f"color: {ACCENT_HI}; font-size: 18px;")
        v.addWidget(tt)

        sub = QLabel("Please wait while we check the records.")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 16px;")
        v.addWidget(sub)
        v.addStretch(1)
