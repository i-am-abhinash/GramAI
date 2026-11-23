"""Listening screen: single shared glass orb and consistent home-style controls."""
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPointF
from PyQt6.QtGui import QPainter, QPen, QColor
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from widgets.components import MicButton, GlassButton
from widgets.aurora import AuroraSurface
import math

class ListeningOrb(MicButton):
    """One optical glass orb, with audio ticks drawn outside the glass rim."""
    def __init__(self):
        super().__init__(diameter=208)
        self.setFixedSize(350, 350)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet("background: transparent;")
        self.detected=False
        self.phase=0
        self.wave_timer=QTimer(self)
        self.wave_timer.timeout.connect(self.animate)
        self.wave_timer.start(65)

    def animate(self):
        self.phase += 1
        self.update()

    def set_voice_detected(self, detected):
        self.detected=detected
        self.update()

    def paintEvent(self, event):
        # MicButton paints exactly one glass sphere, at the center of this widget.
        super().paintEvent(event)
        p=QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        cx=cy=175
        for i in range(44):
            angle=(i/44)*math.tau
            strength=(.5+.5*math.sin(self.phase*.20+i*.62)) if self.detected else .30
            inner=135
            outer=inner+9+strength*(17 if self.detected else 7)
            pen=QPen(QColor("#20DDF7") if i<22 else QColor("#C15BFF"),4)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(pen)
            p.drawLine(QPointF(cx+math.cos(angle)*inner,cy+math.sin(angle)*inner),
                       QPointF(cx+math.cos(angle)*outer,cy+math.sin(angle)*outer))

class ListeningScreen(QWidget):
    cancelled=pyqtSignal()
    home_requested=pyqtSignal()

    def __init__(self,parent=None):
        super().__init__(parent)
        root=QVBoxLayout(self);root.setContentsMargins(0,0,0,0)
        surface=AuroraSurface();root.addWidget(surface)
        v=QVBoxLayout(surface);v.setContentsMargins(35,18,35,35);v.setSpacing(13)

        top=QHBoxLayout();top.setSpacing(14)
        menu=GlassButton("☰");menu.setFixedSize(48,46)
        menu.setToolTip("Return to Home")
        menu.clicked.connect(self.home_requested.emit)
        top.addWidget(menu)
        brand=QLabel("Gram<span style='color:#42DFFF'>AI</span>")
        brand.setStyleSheet("background:transparent;color:white;font-size:26px;font-weight:800;")
        top.addWidget(brand);top.addStretch()
        self.telugu=GlassButton("తెలుగు",pill=True)
        self.english=GlassButton("English",pill=True)
        for b in (self.telugu,self.english):
            b.setCheckable(True);b.setFixedSize(90,40)
            top.addWidget(b)
        self.telugu.setChecked(True)
        self.telugu.clicked.connect(lambda:self._language(True))
        self.english.clicked.connect(lambda:self._language(False))
        v.addLayout(top)
        v.addStretch(1)

        self.orb=ListeningOrb()
        self.wave=self.orb  # compatibility with existing controller calls
        v.addWidget(self.orb,alignment=Qt.AlignmentFlag.AlignHCenter)
        self.t1=QLabel();self.t1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.t1.setStyleSheet("background:transparent;color:#F7FBFF;font-size:30px;font-weight:700;")
        v.addWidget(self.t1)
        self.t2=QLabel();self.t2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.t2.setStyleSheet("background:transparent;color:#7CE9FF;font-size:21px;")
        v.addWidget(self.t2)
        self.hint=QLabel();self.hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hint.setStyleSheet("background:transparent;color:#D2DFF4;font-size:16px;")
        v.addWidget(self.hint)
        cancel=GlassButton("✕  Cancel",pill=True)
        cancel.setFixedSize(220,52)
        cancel.clicked.connect(self.cancelled.emit)
        v.addWidget(cancel,alignment=Qt.AlignmentFlag.AlignHCenter)
        v.addStretch(1)
        self._language(True)

    def _language(self,telugu):
        self.telugu.setChecked(telugu)
        self.english.setChecked(not telugu)
        self.t1.setText("🎙  వింటున్నాను..." if telugu else "🎙  Listening...")
        self.t2.setText("నేను వింటున్నాను... మీ ప్రశ్న అడగండి" if telugu else "I'm listening... ask your question")
        self.hint.setText("దయచేసి స్పష్టంగా మాట్లాడండి. ఆపడానికి Cancel నొక్కండి." if telugu else "Speak clearly. Press Cancel to stop.")

    def set_voice_detected(self,detected:bool):
        self.orb.set_voice_detected(detected)
        if detected:
            self.t1.setText("✓  వాయిస్ గుర్తించబడింది" if self.telugu.isChecked() else "✓  Voice Detected")
        else:
            self._language(self.telugu.isChecked())
