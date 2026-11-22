"""Admin dashboard with stat cards + most-asked questions panel."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QFrame, QLabel, QGraphicsDropShadowEffect)
from PyQt6.QtGui import QColor
from theme import PANEL, PANEL_HI, BORDER, ACCENT, ACCENT_HI, SUCCESS, WARNING, TEXT, TEXT_MUTED


def stat_card(title, value, delta, color):
    c = QFrame(); c.setObjectName("Card")
    c.setStyleSheet(f"QFrame#Card {{background:rgba(23,44,76,0.91); border:1px solid #43658B; border-radius:20px;}}")
    sh = QGraphicsDropShadowEffect(c); sh.setBlurRadius(30); sh.setOffset(0,6); sh.setColor(QColor(0,0,0,120))
    c.setGraphicsEffect(sh)
    v = QVBoxLayout(c); v.setContentsMargins(22,18,22,18); v.setSpacing(6)
    t = QLabel(title); t.setStyleSheet(f"color:{TEXT_MUTED}; font-size:13px; font-weight:600; letter-spacing:0.5px;")
    val = QLabel(value); val.setStyleSheet(f"color:{TEXT}; font-size:34px; font-weight:800;")
    d = QLabel(delta); d.setStyleSheet(f"color:{color}; font-size:13px; font-weight:600;")
    v.addWidget(t); v.addWidget(val); v.addWidget(d)
    return c


class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.v = QVBoxLayout(self); self.v.setContentsMargins(30,28,30,28); self.v.setSpacing(20)

        head = QLabel("Dashboard")
        head.setStyleSheet(f"color:{TEXT}; font-size:26px; font-weight:800;")
        self.v.addWidget(head)
        sub = QLabel("Overview of kiosk activity")
        sub.setStyleSheet(f"color:{TEXT_MUTED}; font-size:14px;")
        self.v.addWidget(sub)

        self.grid = QGridLayout(); self.grid.setSpacing(18)
        self.v.addLayout(self.grid)

        # Most asked
        self.wrap = QFrame(); self.wrap.setObjectName("Card")
        self.wrap.setStyleSheet(f"QFrame#Card {{background:rgba(23,44,76,0.91); border:1px solid #43658B; border-radius:20px;}}")
        self.wv = QVBoxLayout(self.wrap); self.wv.setContentsMargins(22,18,22,18); self.wv.setSpacing(10)
        wt = QLabel("Most Asked Questions")
        wt.setStyleSheet(f"color:{TEXT}; font-size:18px; font-weight:700;")
        self.wv.addWidget(wt)
        
        self.v.addWidget(self.wrap)
        self.v.addStretch(1)
        
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
            row.setStyleSheet(f"QFrame#Card {{background:rgba(31,58,96,0.92); border:1px solid #43658B; border-radius:18px;}}")
            h = QHBoxLayout(row); h.setContentsMargins(16,12,16,12)
            qq = QLabel(str(q)); qq.setStyleSheet(f"color:{TEXT}; font-size:15px;")
            count = QLabel(f"{n} asks")
            count.setStyleSheet(f"color:{ACCENT_HI}; background:rgba(59,130,246,40);"
                                f"border-radius:10px; padding:4px 10px; font-size:12px; font-weight:700;")
            h.addWidget(qq, 1); h.addWidget(count)
            self.wv.addWidget(row)
