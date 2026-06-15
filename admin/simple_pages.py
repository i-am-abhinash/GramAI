"""Lightweight placeholder pages for sections we haven't fully fleshed out."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from theme import PANEL, BORDER, TEXT, TEXT_MUTED, ACCENT_HI


class SimplePage(QWidget):
    def __init__(self, title: str, description: str, parent=None):
        super().__init__(parent)
        v = QVBoxLayout(self); v.setContentsMargins(30,28,30,28); v.setSpacing(14)

        t = QLabel(title); t.setStyleSheet(f"color:{TEXT}; font-size:26px; font-weight:800;")
        v.addWidget(t)
        s = QLabel(description); s.setStyleSheet(f"color:{TEXT_MUTED}; font-size:14px;")
        v.addWidget(s)

        card = QFrame(); card.setObjectName("Card")
        card.setStyleSheet(f"QFrame#Card {{background:{PANEL}; border:1px solid {BORDER}; border-radius:16px;}}")
        cv = QVBoxLayout(card); cv.setContentsMargins(40,40,40,40)
        info = QLabel(f"✨  {title} module")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setStyleSheet(f"color:{ACCENT_HI}; font-size:20px; font-weight:700;")
        hint = QLabel("UI scaffold ready — connect to your backend service to enable.")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setStyleSheet(f"color:{TEXT_MUTED}; font-size:13px;")
        cv.addStretch(1); cv.addWidget(info); cv.addWidget(hint); cv.addStretch(1)
        v.addWidget(card, 1)
