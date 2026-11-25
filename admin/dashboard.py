"""Admin dashboard with stat cards + most-asked questions panel."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QFrame, QLabel, QGraphicsDropShadowEffect, QSizePolicy)
from PyQt6.QtGui import QColor
from theme import PANEL, PANEL_HI, BORDER, ACCENT, ACCENT_HI, SUCCESS, WARNING, TEXT, TEXT_MUTED
from admin.glass import ADMIN_QSS, SURFACE, ROW, EDGE, badge, glass_button, set_cell, GlassDialog, confirm


def stat_card(title, value, delta, color):
    c = QFrame(); c.setObjectName("Card")
    c.setStyleSheet("QFrame#Card { background: " + SURFACE + "; border: 1px solid " + EDGE + "; border-radius: 20px; } QLabel { background: transparent; border: none; }")
    sh = QGraphicsDropShadowEffect(c); sh.setBlurRadius(30); sh.setOffset(0,6); sh.setColor(QColor(0,0,0,120))
    c.setGraphicsEffect(sh)
    v = QVBoxLayout(c); v.setContentsMargins(18,12,18,12); v.setSpacing(4)
    t = QLabel(title); t.setStyleSheet(f"color:{TEXT_MUTED}; font-size:13px; font-weight:600; letter-spacing:0.5px;")
    val = QLabel(value); val.setStyleSheet(f"color:{TEXT}; font-size:34px; font-weight:800;")
    d = QLabel(delta); d.setStyleSheet(f"color:{color}; font-size:13px; font-weight:600;")
    v.addWidget(t); v.addWidget(val); v.addWidget(d)
    return c


class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Scope transparent typography and dark glass surfaces to this page.
        self.setObjectName("AdminContentPage")
        self.setStyleSheet(ADMIN_QSS)

        self.v = QVBoxLayout(self); self.v.setContentsMargins(24,18,24,20); self.v.setSpacing(12)

        head = QLabel("Dashboard")
        head.setStyleSheet(f"color:{TEXT}; font-family: Segoe UI Variable; font-size:30px; font-weight:800;")
        self.v.addWidget(head)
        sub = QLabel("Overview of kiosk activity")
        sub.setStyleSheet(f"color:{TEXT_MUTED}; font-size:14px;")
        self.v.addWidget(sub)

        self.grid = QGridLayout(); self.grid.setSpacing(14)
        self.v.addLayout(self.grid)

        # Most asked
        self.wrap = QFrame(); self.wrap.setObjectName("Card")
        self.wrap.setStyleSheet("QFrame#Card { background: " + SURFACE + "; border: 1px solid " + EDGE + "; border-radius: 20px; }")
        self.wv = QVBoxLayout(self.wrap); self.wv.setContentsMargins(16,12,16,12); self.wv.setSpacing(6)
        wt = QLabel("Most Asked Questions")
        wt.setStyleSheet(f"color:{TEXT}; font-size:18px; font-weight:700;")
        self.wv.addWidget(wt)
        
        from PyQt6.QtWidgets import QScrollArea
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea, QScrollArea QWidget#qt_scrollarea_viewport { background: transparent; border: none; }")
        scroll.setWidget(self.wrap)
        self.v.addWidget(scroll, 1)
        
        self.refresh_data()
        
    def refresh_data(self):
        # Clear grid
        for i in reversed(range(self.grid.count())): 
            widget = self.grid.itemAt(i).widget()
            if widget: widget.deleteLater()
            
        # clear most asked
        for i in reversed(range(1, self.wv.count())): # keep title at index 0
            widget = self.wv.itemAt(i).widget()
            if widget: widget.deleteLater()

        from backend.services.admin_service import AdminService
        admin_service = AdminService()
        sync_stats = admin_service.get_dashboard_stats()
        
        self.grid.addWidget(stat_card("Total Questions", str(sync_stats.get('total_questions', 0)), "▲ Overall Volume", ACCENT_HI), 0, 0)
        self.grid.addWidget(stat_card("Answered Questions", str(sync_stats.get('answered_questions', 0)), "▲ System Served", SUCCESS), 0, 1)
        self.grid.addWidget(stat_card("Unanswered Questions", str(sync_stats.get('unanswered_questions', 0)), "▼ Pending Review", WARNING), 0, 2)
        self.grid.addWidget(stat_card("Flagged Responses", str(sync_stats.get('flagged_responses', 0)), "▼ Unhelpful", "#ff4d4f"), 0, 3)

        from backend.services.dashboard_service import DashboardService
        most_asked = DashboardService().get_most_asked(limit=5)
        if not most_asked:
            most_asked = [("No questions recorded yet.", 0)]
            
        for q, n in most_asked:
            row = QFrame(); row.setObjectName("Card")
            row.setStyleSheet("QFrame#Card { background: " + ROW + "; border: 1px solid #4369A0; border-radius: 12px; }")
            h = QHBoxLayout(row); h.setContentsMargins(12,5,12,5); h.setSpacing(10)
            qq = QLabel(str(q)); qq.setWordWrap(True); qq.setMinimumHeight(28)
            qq.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            qq.setStyleSheet(f"color:{TEXT}; font-size:15px; background:transparent; border:none;")
            count = badge(f"{n} time" if n == 1 else f"{n} times")
            h.addWidget(qq, 1); h.addWidget(count)
            self.wv.addWidget(row)
