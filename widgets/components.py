"""Reusable custom widgets: animated mic button, voice wave viz, status pills, quick-access card."""
import math, random
from PyQt6.QtCore import (Qt, QTimer, QSize, QRectF, QPropertyAnimation,
                          pyqtProperty, pyqtSignal, QPointF)
from PyQt6.QtGui  import (QPainter, QColor, QPen, QBrush, QRadialGradient,
                          QLinearGradient, QFont, QPainterPath)
from PyQt6.QtWidgets import (QWidget, QFrame, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QSizePolicy, QGraphicsDropShadowEffect)
from theme import ACCENT, ACCENT_HI, PANEL, PANEL_HI, BORDER, TEXT, TEXT_MUTED, SUCCESS, WARNING, DANGER


# ---------------------------------------------------------------------------
# Simple, accessible microphone button (IDLE STATE)
# ---------------------------------------------------------------------------
class MicButton(QWidget):
    clicked = pyqtSignal()

    def __init__(self, diameter: int = 180, parent=None):
        super().__init__(parent)
        self._d = diameter
        self.setFixedSize(diameter + 60, diameter + 60)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._pulse = 0.0
        self._timer = QTimer(self); self._timer.timeout.connect(self._tick); self._timer.start(50)

    def _tick(self):
        self._pulse = (self._pulse + 0.015) % 1.0
        self.update()

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        cx, cy = self.width() / 2, self.height() / 2
        r = self._d / 2

        # Glowing Aura
        breathe = math.sin(self._pulse * math.tau) * 0.5 + 0.5
        aura_r = r + 10 + (breathe * 20)
        
        g_aura = QRadialGradient(QPointF(cx, cy), aura_r)
        g_aura.setColorAt(0.0, QColor(0, 229, 255, 80))  # Cyan aura
        g_aura.setColorAt(0.5, QColor(138, 43, 226, 40)) # Purple glow
        g_aura.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.setBrush(QBrush(g_aura))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(cx, cy), aura_r, aura_r)

        # Dark Metallic Orb
        g_orb = QRadialGradient(QPointF(cx - r*0.3, cy - r*0.3), r * 1.5)
        g_orb.setColorAt(0.0, QColor(80, 80, 100))
        g_orb.setColorAt(0.5, QColor(30, 30, 40))
        g_orb.setColorAt(1.0, QColor(10, 10, 15))
        p.setBrush(QBrush(g_orb))
        
        # Subtle glowing rim
        p.setPen(QPen(QColor(0, 229, 255, 100), 2))
        p.drawEllipse(QPointF(cx, cy), r, r)

        # Simple white microphone icon inside the orb
        p.setBrush(QBrush(QColor(255, 255, 255, 180)))
        p.setPen(Qt.PenStyle.NoPen)
        mw, mh = r * 0.3, r * 0.5
        p.drawRoundedRect(QRectF(cx - mw/2, cy - mh/2 - r*0.05, mw, mh), mw/2, mw/2)
        pen = QPen(QColor(255, 255, 255, 180), 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        p.setPen(pen); p.setBrush(Qt.BrushStyle.NoBrush)
        arc_r = r * 0.4
        p.drawArc(QRectF(cx - arc_r, cy - arc_r*0.6, arc_r*2, arc_r*2), 200*16, 140*16)
        p.drawLine(QPointF(cx, cy + arc_r*0.85), QPointF(cx, cy + r*0.7))
        p.drawLine(QPointF(cx - r*0.15, cy + r*0.7), QPointF(cx + r*0.15, cy + r*0.7))


# ---------------------------------------------------------------------------
# Circular audio wave visualization (used on Listening screen)
# ---------------------------------------------------------------------------
class VoiceWaveCircle(QWidget):
    def __init__(self, parent=None, bars: int = 40):
        super().__init__(parent)
        self._n = bars
        self._levels = [0.1] * bars
        self.setMinimumSize(360, 360)
        self._timer = QTimer(self); self._timer.timeout.connect(self._tick); self._timer.start(50)
        self._phase = 0
        self._voice_detected = False

    def set_voice_detected(self, detected: bool):
        self._voice_detected = detected

    def _tick(self):
        self._phase += 1
        if self._voice_detected:
            # Active waveform
            self._levels = [
                0.3 + 0.7 * abs(math.sin(self._phase * 0.15 + i * 0.4)) * random.uniform(0.5, 1.0)
                for i in range(self._n)
            ]
        else:
            # Gentle idle ripple
            self._levels = [
                0.15 + 0.1 * math.sin(self._phase * 0.05 + i * 0.1)
                for i in range(self._n)
            ]
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        cx, cy = self.width()/2, self.height()/2
        rmin = min(self.width(), self.height()) * 0.25
        rmax_base = min(self.width(), self.height()) * 0.45

        # Dynamic background ring/aura
        g = QRadialGradient(QPointF(cx, cy), rmax_base)
        g.setColorAt(0.4, QColor(0, 229, 255, 40 if self._voice_detected else 20))
        g.setColorAt(0.8, QColor(138, 43, 226, 30 if self._voice_detected else 10))
        g.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.setBrush(QBrush(g)); p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(cx, cy), rmax_base, rmax_base)

        # Dynamic waveform bars
        for i, lvl in enumerate(self._levels):
            angle = (i / self._n) * math.tau
            r2 = rmin + (rmax_base - rmin) * lvl
            x1 = cx + math.cos(angle) * rmin
            y1 = cy + math.sin(angle) * rmin
            x2 = cx + math.cos(angle) * r2
            y2 = cy + math.sin(angle) * r2
            
            # Use gradient per line or just solid purple/cyan
            pen = QPen(QColor(0, 229, 255, 180) if i % 2 == 0 else QColor(138, 43, 226, 180))
            pen.setWidth(4); pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(pen)
            p.drawLine(QPointF(x1,y1), QPointF(x2,y2))

        # inner Dark Metallic Orb
        orb_r = rmin * 0.85
        g_orb = QRadialGradient(QPointF(cx - orb_r*0.3, cy - orb_r*0.3), orb_r * 1.5)
        g_orb.setColorAt(0.0, QColor(80, 80, 100))
        g_orb.setColorAt(0.5, QColor(30, 30, 40))
        g_orb.setColorAt(1.0, QColor(10, 10, 15))
        p.setBrush(QBrush(g_orb))
        p.setPen(QPen(QColor(0, 229, 255, 120), 2))
        p.drawEllipse(QPointF(cx, cy), orb_r, orb_r)

        # simple mic icon inside
        p.setBrush(QBrush(QColor(255, 255, 255, 180)))
        p.setPen(Qt.PenStyle.NoPen)
        mw, mh = orb_r * 0.3, orb_r * 0.5
        p.drawRoundedRect(QRectF(cx - mw/2, cy - mh/2 - orb_r*0.05, mw, mh), mw/2, mw/2)
        pen_mic = QPen(QColor(255, 255, 255, 180), 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        p.setPen(pen_mic); p.setBrush(Qt.BrushStyle.NoBrush)
        arc_r = orb_r * 0.4
        p.drawArc(QRectF(cx - arc_r, cy - arc_r*0.6, arc_r*2, arc_r*2), 200*16, 140*16)
        p.drawLine(QPointF(cx, cy + arc_r*0.85), QPointF(cx, cy + orb_r*0.7))
        p.drawLine(QPointF(cx - orb_r*0.15, cy + orb_r*0.7), QPointF(cx + orb_r*0.15, cy + orb_r*0.7))


# ---------------------------------------------------------------------------
# Simple progress spinner (Processing state)
# ---------------------------------------------------------------------------
class ThinkingSpinner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(120, 120)
        self._a = 0.0
        self._t = QTimer(self); self._t.timeout.connect(self._tick); self._t.start(20)

    def _tick(self):
        self._a = (self._a + 5) % 360
        self.update()

    def paintEvent(self, _):
        p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        cx, cy = self.width()/2, self.height()/2
        r = min(self.width(), self.height())/2 - 12
        
        # Glowing Aura background
        g_aura = QRadialGradient(QPointF(cx, cy), r * 1.5)
        g_aura.setColorAt(0.0, QColor(0, 229, 255, 30))
        g_aura.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.setBrush(QBrush(g_aura))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(cx, cy), r * 1.5, r * 1.5)

        # inner Dark Metallic Orb
        orb_r = r * 0.85
        g_orb = QRadialGradient(QPointF(cx - orb_r*0.3, cy - orb_r*0.3), orb_r * 1.5)
        g_orb.setColorAt(0.0, QColor(80, 80, 100))
        g_orb.setColorAt(0.5, QColor(30, 30, 40))
        g_orb.setColorAt(1.0, QColor(10, 10, 15))
        p.setBrush(QBrush(g_orb))
        p.setPen(QPen(QColor(0, 229, 255, 80), 2))
        p.drawEllipse(QPointF(cx, cy), orb_r, orb_r)
        
        # simple mic icon inside
        p.setBrush(QBrush(QColor(255, 255, 255, 180)))
        p.setPen(Qt.PenStyle.NoPen)
        mw, mh = orb_r * 0.3, orb_r * 0.5
        p.drawRoundedRect(QRectF(cx - mw/2, cy - mh/2 - orb_r*0.05, mw, mh), mw/2, mw/2)
        pen_mic = QPen(QColor(255, 255, 255, 180), 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        p.setPen(pen_mic); p.setBrush(Qt.BrushStyle.NoBrush)
        arc_r = orb_r * 0.4
        p.drawArc(QRectF(cx - arc_r, cy - arc_r*0.6, arc_r*2, arc_r*2), 200*16, 140*16)
        p.drawLine(QPointF(cx, cy + arc_r*0.85), QPointF(cx, cy + orb_r*0.7))
        p.drawLine(QPointF(cx - orb_r*0.15, cy + orb_r*0.7), QPointF(cx + orb_r*0.15, cy + orb_r*0.7))
        
        # Rotating progress arc (Cyan/Purple gradient)
        p.setBrush(Qt.BrushStyle.NoBrush)
        pen_arc = QPen(QColor(0, 229, 255, 200)) # Cyan glow
        pen_arc.setWidth(6)
        pen_arc.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen_arc)
        p.drawArc(QRectF(cx - r, cy - r, r * 2, r * 2), int(-self._a * 16), 140 * 16)
        
        pen_arc_blue = QPen(QColor(138, 43, 226, 200)) # Purple tail
        pen_arc_blue.setWidth(4)
        pen_arc_blue.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen_arc_blue)
        p.drawArc(QRectF(cx - r, cy - r, r * 2, r * 2), int((-self._a - 40) * 16), 80 * 16)


# ---------------------------------------------------------------------------
# Quick-access card with hover lift + glow
# ---------------------------------------------------------------------------
class QuickAccessCard(QFrame):
    clicked = pyqtSignal(str)

    def __init__(self, title: str, subtitle: str, emoji: str, key: str, parent=None):
        super().__init__(parent)
        self._key = key
        self.setObjectName("CardHover")
        self.setProperty("class", "Card")
        self.setMinimumSize(220, 200)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QFrame#CardHover {{
                background-color: {PANEL};
                border: 1px solid rgba(255,255,255,0.05);
                border-radius: 20px;
            }}
            QFrame#CardHover:hover {{
                background-color: {PANEL_HI};
                border: 1px solid {ACCENT};
            }}
        """)

        v = QVBoxLayout(self); v.setContentsMargins(22,22,22,22); v.setSpacing(12)

        icon_lbl = QLabel(emoji)
        icon_lbl.setStyleSheet(f"font-size: 44px;")
        v.addWidget(icon_lbl)

        title_lbl = QLabel(title); title_lbl.setObjectName("H3")
        title_lbl.setStyleSheet("font-size: 20px; font-weight: 700;")
        v.addWidget(title_lbl)

        sub_lbl = QLabel(subtitle); sub_lbl.setObjectName("Muted")
        sub_lbl.setWordWrap(True)
        v.addWidget(sub_lbl)
        v.addStretch(1)

        chev = QLabel("Open  →")
        chev.setStyleSheet(f"color: {ACCENT_HI}; font-weight:600; font-size: 14px;")
        v.addWidget(chev)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._key)


# ---------------------------------------------------------------------------
# Status pill widget
# ---------------------------------------------------------------------------
class StatusPill(QFrame):
    def __init__(self, label: str, ok: bool = True, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self.setStyleSheet(f"""
            QFrame#Card {{
                background-color: {PANEL};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)
        h = QHBoxLayout(self); h.setContentsMargins(14,8,14,8); h.setSpacing(10)
        dot = QLabel("●")
        dot.setStyleSheet(f"color: {SUCCESS if ok else WARNING}; font-size: 16px;")
        txt = QLabel(label); txt.setStyleSheet(f"color: {TEXT}; font-size: 13px; font-weight: 600;")
        h.addWidget(dot); h.addWidget(txt)
