"""Listening overlay screen with circular wave viz."""
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from widgets.components import VoiceWaveCircle
from theme import TEXT, ACCENT_HI, TEXT_MUTED


class ListeningScreen(QWidget):
    cancelled = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        v = QVBoxLayout(self); v.setContentsMargins(40,40,40,40); v.setSpacing(18)
        v.addStretch(1)

        self.wave = VoiceWaveCircle(); self.wave.setFixedSize(420, 420)
        v.addWidget(self.wave, alignment=Qt.AlignmentFlag.AlignHCenter)

        from backend.locale.i18n import I18n
        
        self.t1 = QLabel(I18n.get("listen_listening")); self.t1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.t1.setStyleSheet(f"color: {TEXT}; font-size: 32px; font-weight: 700;")
        v.addWidget(self.t1)

        self.t2 = QLabel(I18n.get("listen_telugu"))
        self.t2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.t2.setStyleSheet(f"color: {ACCENT_HI}; font-size: 20px;")
        v.addWidget(self.t2)

        self.hint = QLabel(I18n.get("listen_hint"))
        self.hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hint.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 16px;")
        v.addWidget(self.hint)

    def set_voice_detected(self, detected: bool):
        from backend.locale.i18n import I18n
        self.wave.set_voice_detected(detected)
        if detected:
            self.t1.setText(I18n.get("listen_detected"))
            self.t1.setStyleSheet(f"color: #10B981; font-size: 32px; font-weight: 700;")
        else:
            self.t1.setText(I18n.get("listen_listening"))
            self.t1.setStyleSheet(f"color: {TEXT}; font-size: 32px; font-weight: 700;")

        cancel = QPushButton(I18n.get("cancel")); cancel.setObjectName("Ghost")
        cancel.setFixedWidth(180); cancel.setFixedHeight(48)
        cancel.clicked.connect(self.cancelled.emit)
        v.addWidget(cancel, alignment=Qt.AlignmentFlag.AlignHCenter)
        v.addStretch(1)
