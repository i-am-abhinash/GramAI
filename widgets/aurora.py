"""Shared GramAI backdrop with optional approved image asset."""
from pathlib import Path
from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QPainter, QColor, QLinearGradient, QRadialGradient, QPixmap
from PyQt6.QtWidgets import QWidget

class AuroraSurface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._backdrop = QPixmap(str(Path(__file__).resolve().parent.parent / "assets" / "sapphire_background.png"))

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        w, h = self.width(), self.height()
        if not w or not h:
            return
        if not self._backdrop.isNull():
            p.drawPixmap(self.rect(), self._backdrop)
            return
        base = QLinearGradient(0, 0, 0, h)
        base.setColorAt(0, QColor("#0A1734"))
        base.setColorAt(1, QColor("#030509"))
        p.fillRect(self.rect(), base)
        for x, y, color in [(0.05, 0.04, QColor(36,107,253,95)), (.95,.08,QColor(65,105,255,85))]:
            r = min(w,h)*.65
            glow = QRadialGradient(QPointF(w*x,h*y),r)
            glow.setColorAt(0,color)
            glow.setColorAt(1,QColor(0,0,0,0))
            p.fillRect(self.rect(),glow)
