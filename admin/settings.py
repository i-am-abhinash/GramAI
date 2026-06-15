"""Settings page."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QFormLayout, QComboBox, QLineEdit)
from theme import PANEL, BORDER, TEXT, TEXT_MUTED, PANEL_HI

class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        v = QVBoxLayout(self); v.setContentsMargins(30,28,30,28); v.setSpacing(16)

        head_row = QHBoxLayout()
        head = QLabel("Settings")
        head.setStyleSheet(f"color:{TEXT}; font-size:26px; font-weight:800;")
        head_row.addWidget(head); head_row.addStretch(1)
        save = QPushButton("Save Settings"); save.setObjectName("Primary"); save.setMinimumHeight(42)
        head_row.addWidget(save)
        v.addLayout(head_row)

        sub = QLabel("Configure language, voice models, and kiosk preferences.")
        sub.setStyleSheet(f"color:{TEXT_MUTED}; font-size:14px;")
        v.addWidget(sub)

        # Settings Form
        card = QFrame(); card.setObjectName("Card")
        card.setStyleSheet(f"QFrame#Card {{background:{PANEL}; border:1px solid {BORDER}; border-radius:16px;}}")
        form = QFormLayout(card); form.setContentsMargins(30,30,30,30); form.setSpacing(20)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # Voice Language
        lang = QComboBox(); lang.addItems(["Telugu (te-IN)", "Hindi (hi-IN)", "English (en-IN)"])
        lang.setMinimumHeight(40); lang.setStyleSheet(f"background:{PANEL_HI}; color:{TEXT}; padding-left:10px;")
        lbl1 = QLabel("Voice Assistant Language:"); lbl1.setStyleSheet(f"color:{TEXT}; font-weight:700;")
        form.addRow(lbl1, lang)

        # Speech Engine
        engine = QComboBox(); engine.addItems(["Google Speech-to-Text", "Vosk (Offline)", "OpenAI Whisper"])
        engine.setMinimumHeight(40); engine.setStyleSheet(f"background:{PANEL_HI}; color:{TEXT}; padding-left:10px;")
        lbl2 = QLabel("Speech Recognition Engine:"); lbl2.setStyleSheet(f"color:{TEXT}; font-weight:700;")
        form.addRow(lbl2, engine)

        # Admin Password
        pw = QLineEdit(); pw.setPlaceholderText("Enter new admin password"); pw.setEchoMode(QLineEdit.EchoMode.Password)
        pw.setMinimumHeight(40)
        lbl3 = QLabel("Update Admin Password:"); lbl3.setStyleSheet(f"color:{TEXT}; font-weight:700;")
        form.addRow(lbl3, pw)

        v.addWidget(card)
        v.addStretch(1)
