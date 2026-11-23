"""Shared midnight aurora surface for GramAI feature windows."""
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QPainterPath, QLinearGradient, QRadialGradient
from PyQt6.QtWidgets import QWidget

class AuroraSurface(QWidget):
    def paintEvent(self, event):
        p=QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w,h=self.width(),self.height()
        if not w or not h: return
        base=QLinearGradient(0,0,w,h)
        base.setColorAt(0,QColor("#020918")); base.setColorAt(.6,QColor("#03091B")); base.setColorAt(1,QColor("#0B0724"))
        p.fillRect(self.rect(),base)
        p.setPen(Qt.PenStyle.NoPen)
        for x,y,r,c in [(.10,.76,.48,QColor(0,172,255,43)),(.92,.64,.46,QColor(180,45,255,42))]:
            rad=min(w,h)*r
            glow=QRadialGradient(QPointF(w*x,h*y),rad)
            glow.setColorAt(0,c); glow.setColorAt(1,QColor(0,0,0,0))
            p.setBrush(glow); p.drawEllipse(QPointF(w*x,h*y),rad,rad)
        # Two low, layered light ribbons; deliberately no top semicircular arc.
        for n in range(3):
            y=h*(.80+n*.065)
            path=QPainterPath(QPointF(-20,y))
            path.cubicTo(w*.23,y-h*.23,w*.40,y+h*.16,w*.61,y+h*.03)
            path.cubicTo(w*.81,y-h*.10,w*.90,y-h*.28,w+20,y-h*.30)
            g=QLinearGradient(0,y,w,y)
            g.setColorAt(0,QColor(0,208,255,125-n*28))
            g.setColorAt(.55,QColor(29,93,244,68))
            g.setColorAt(1,QColor(224,69,255,125-n*28))
            p.setPen(QPen(g,2.2 if n==0 else 1.1))
            p.setBrush(Qt.BrushStyle.NoBrush);p.drawPath(path)
