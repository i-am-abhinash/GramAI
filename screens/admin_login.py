"""Admin login screen."""
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel,
                             QLineEdit, QPushButton, QGraphicsDropShadowEffect)
from PyQt6.QtGui import QColor
from theme import PANEL, BORDER, ACCENT_HI, TEXT, TEXT_MUTED
from widgets.components import GlassButton
from widgets.aurora import AuroraSurface


class AdminLoginScreen(QWidget):
    login_ok   = pyqtSignal()
    back       = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        root=QVBoxLayout(self); root.setContentsMargins(0,0,0,0)
        surface=AuroraSurface(); root.addWidget(surface)
        v=QVBoxLayout(surface); v.setContentsMargins(40,40,40,40)
        v.addStretch(1)

        card = QFrame(); card.setObjectName("Card")
        card.setFixedWidth(500)
        card.setStyleSheet("QFrame#Card {background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #101B32,stop:.5 #0A1020,stop:1 #15264B);border:1px solid #246BFD;border-radius:26px;}")
        sh = QGraphicsDropShadowEffect(self); sh.setBlurRadius(60); sh.setOffset(0,16); sh.setColor(QColor(0,0,0,180))
        card.setGraphicsEffect(sh)

        cv = QVBoxLayout(card); cv.setContentsMargins(38,30,38,32); cv.setSpacing(16)

        lock = QLabel("🏛️"); lock.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lock.setStyleSheet("background:transparent;font-size: 42px;")
        cv.addWidget(lock)

        t = QLabel("Secure Government Login"); t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t.setStyleSheet(f"background:transparent;color: {TEXT}; font-size: 24px; font-weight: 700;")
        cv.addWidget(t)
        s = QLabel("Authorized Village Officials Only"); s.setAlignment(Qt.AlignmentFlag.AlignCenter)
        s.setStyleSheet(f"background:transparent;color: {TEXT_MUTED}; font-size: 14px;")
        cv.addWidget(s)
        
        self.error_label = QLabel(""); self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setStyleSheet("background:transparent;color:#FF858C;font-size:13px;font-weight:600;")
        self.error_label.hide()
        cv.addWidget(self.error_label)

        cv.addSpacing(8)
        self.user = QLineEdit(); self.user.setPlaceholderText("Username"); self.user.setMinimumHeight(46)
        self.pwd  = QLineEdit(); self.pwd.setPlaceholderText("Password"); self.pwd.setMinimumHeight(46)
        self.pwd.setEchoMode(QLineEdit.EchoMode.Password)
        cv.addWidget(self.user); cv.addWidget(self.pwd)

        login = GlassButton("➜  Authenticate", pill=True); login.setObjectName("Primary"); login.setMinimumHeight(48)
        login.clicked.connect(self._handle_login)
        cv.addWidget(login)

        back = GlassButton("← Back to Voice Assistant", pill=True); back.setObjectName("Ghost")
        back.clicked.connect(self.back.emit)
        cv.addWidget(back)

        row = QHBoxLayout(); row.addStretch(1); row.addWidget(card); row.addStretch(1)
        v.addLayout(row)
        v.addStretch(1)

    def _handle_login(self):
        username = self.user.text().strip()
        password = self.pwd.text()
        
        if not username or not password:
            self.error_label.setText("Please enter username and password.")
            self.error_label.show()
            return
            
        from backend.services.auth_service import AuthService
        result = AuthService.authenticate(username, password)
        
        if result["success"]:
            self.error_label.hide()
            self.user.clear()
            self.pwd.clear()
            self.login_ok.emit()
        else:
            self.error_label.setText(result["message"])
            self.error_label.show()
