"""Reusable custom widgets: animated mic button, voice wave viz, status pills, quick-access card."""
import math, random
from PyQt6.QtCore import (Qt, QTimer, QSize, QRectF, QPropertyAnimation,
                          pyqtProperty, pyqtSignal, QPointF)
from PyQt6.QtGui  import (QPainter, QColor, QPen, QBrush, QRadialGradient,
                          QLinearGradient, QFont, QPainterPath)
from PyQt6.QtWidgets import (QWidget, QFrame, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QSizePolicy, QGraphicsDropShadowEffect)
from theme import ACCENT, ACCENT_HI, PANEL, PANEL_HI, BORDER, TEXT, TEXT_MUTED, SUCCESS, WARNING, DANGER


class GlassButton(QPushButton):
    """Reusable optical-glass button using the microphone orb's cyan/violet palette.

    Native QPushButton signals, keyboard focus and checkable state are preserved.
    """
    def __init__(self, text="", parent=None, *, pill=False):
        super().__init__(text, parent)
        self._pill = pill
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(38)
        self.setStyleSheet("background: transparent; border: none; color: white;")
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(2.5, 2.5, -2.5, -2.5)
        if rect.width() <= 0 or rect.height() <= 0:
            return
        radius = rect.height() / 2 if self._pill else min(14, rect.height() * .28)
        active = self.isChecked() or self.isDown()
        hover = self.underMouse()
        # Faint outer glow.
        glow_path = QPainterPath()
        glow_path.addRoundedRect(rect.adjusted(-1.5, -1.5, 1.5, 1.5), radius+1, radius+1)
        p.fillPath(glow_path, QColor(34, 192, 255, 24 if hover or active else 9))
        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)
        glass = QLinearGradient(rect.topLeft(), rect.bottomRight())
        if active:
            glass.setColorAt(0, QColor("#0B5B84"))
            glass.setColorAt(.48, QColor("#1D3B83"))
            glass.setColorAt(1, QColor("#66309A"))
        else:
            glass.setColorAt(0, QColor("#1D456B") if hover else QColor("#183552"))
            glass.setColorAt(.42, QColor("#102441"))
            glass.setColorAt(1, QColor("#2A174B"))
        p.fillPath(path, glass)
        p.save()
        p.setClipPath(path)
        # Refracted highlight: the same top-left glass reflection as the orb.
        reflection = QLinearGradient(rect.left(), rect.top(), rect.left(), rect.center().y())
        reflection.setColorAt(0, QColor(224, 248, 255, 115 if hover else 77))
        reflection.setColorAt(1, QColor(140, 212, 255, 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(reflection)
        p.drawEllipse(QRectF(rect.left()+3, rect.top()-rect.height()*.42,
                            rect.width()*.78, rect.height()*.94))
        p.restore()
        rim = QLinearGradient(rect.topLeft(), rect.bottomRight())
        rim.setColorAt(0, QColor("#27E6FF"))
        rim.setColorAt(.52, QColor("#75A6FF"))
        rim.setColorAt(1, QColor("#C36CFF"))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(rim, 1.8 if hover or active else 1.25))
        p.drawPath(path)
        if self.hasFocus():
            p.setPen(QPen(QColor("#C8F4FF"), 1, Qt.PenStyle.DotLine))
            p.drawRoundedRect(rect.adjusted(4,4,-4,-4), max(2,radius-4), max(2,radius-4))
        p.setPen(QColor("#FFFFFF") if self.isEnabled() else QColor("#8193A9"))
        font = self.font()
        font.setFamily("Segoe UI Variable")
        font.setWeight(QFont.Weight.DemiBold)
        p.setFont(font)
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())


# ---------------------------------------------------------------------------
# Simple, accessible microphone button (IDLE STATE)
# ---------------------------------------------------------------------------
class MicButton(QWidget):
    """Animated Midnight Glass orb, with optical reflections and cyan/violet rim."""
    clicked = pyqtSignal()

    def __init__(self, diameter: int = 180, parent=None):
        super().__init__(parent)
        self._d = diameter
        self.setFixedSize(diameter + 70, diameter + 70)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Tap to speak")
        self._pulse = 0.0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(45)

    def _tick(self):
        self._pulse = (self._pulse + 0.009) % 1.0
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        cx, cy = self.width() / 2, self.height() / 2
        r = self._d / 2
        pulse = (math.sin(self._pulse * math.tau) + 1) / 2

        # Optical halo beyond the glass sphere.
        halo = QRadialGradient(QPointF(cx, cy), r + 33)
        halo.setColorAt(0.48, QColor(28, 165, 245, 15))
        halo.setColorAt(0.72, QColor(29, 188, 255, 47 + int(22 * pulse)))
        halo.setColorAt(0.86, QColor(172, 62, 250, 28))
        halo.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(halo)
        p.drawEllipse(QPointF(cx, cy), r + 33, r + 33)

        # Glass interior: midnight-blue core, cyan refracted lower edge.
        glass = QRadialGradient(QPointF(cx - r * .34, cy - r * .43), r * 1.7)
        glass.setColorAt(0.0, QColor("#234F83"))
        glass.setColorAt(.26, QColor("#12294F"))
        glass.setColorAt(.62, QColor("#09162F"))
        glass.setColorAt(.84, QColor("#15245B"))
        glass.setColorAt(1.0, QColor("#7135AD"))
        p.setBrush(glass)
        rim = QLinearGradient(cx-r, cy+r, cx+r, cy-r)
        rim.setColorAt(0.0, QColor("#17E9FF"))
        rim.setColorAt(.48, QColor("#63B7FF"))
        rim.setColorAt(1.0, QColor("#E05CFF"))
        p.setPen(QPen(rim, 3.5))
        p.drawEllipse(QPointF(cx, cy), r, r)

        # Curved highlights clipped to the orb, like a polished glass lens.
        clip = QPainterPath()
        clip.addEllipse(QPointF(cx, cy), r-3, r-3)
        p.save()
        p.setClipPath(clip)
        gloss = QLinearGradient(cx-r, cy-r, cx+r, cy+r)
        gloss.setColorAt(0.0, QColor(230, 251, 255, 175))
        gloss.setColorAt(.30, QColor(110, 209, 255, 55))
        gloss.setColorAt(.68, QColor(70, 103, 209, 0))
        p.setBrush(gloss)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QRectF(cx-r*.86, cy-r*1.15, r*1.32, r*.95))
        p.setPen(QPen(QColor(179, 240, 255, 140), max(2, r*.025)))
        p.drawArc(QRectF(cx-r*.79, cy-r*.81, r*1.57, r*1.57), 92*16, 91*16)
        p.setPen(QPen(QColor(198, 90, 255, 160), max(2, r*.045)))
        p.drawArc(QRectF(cx-r*.85, cy-r*.86, r*1.70, r*1.70), 305*16, 88*16)
        p.setPen(QPen(QColor(22, 225, 255, 160), max(2, r*.035)))
        p.drawArc(QRectF(cx-r*.80, cy-r*.80, r*1.60, r*1.60), 200*16, 87*16)
        p.restore()

        # White microphone glyph.
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor("#F7FDFF"))
        mw, mh = r * .30, r * .53
        p.drawRoundedRect(QRectF(cx-mw/2, cy-mh*.65, mw, mh), mw/2, mw/2)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(QColor("#F7FDFF"), max(3, r*.052),
                      Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.drawArc(QRectF(cx-r*.29, cy-r*.22, r*.58, r*.70), 180*16, 180*16)
        p.drawLine(QPointF(cx, cy+r*.49), QPointF(cx, cy+r*.66))
        p.drawLine(QPointF(cx-r*.15, cy+r*.66), QPointF(cx+r*.15, cy+r*.66))


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
