"""Admin dashboard with stat cards + most-asked questions panel."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QFrame, QLabel, QGraphicsDropShadowEffect, QSizePolicy)
from PyQt6.QtGui import QColor
from theme import PANEL, PANEL_HI, BORDER, ACCENT, ACCENT_HI, SUCCESS, WARNING, TEXT, TEXT_MUTED


def stat_card(title, value, delta, color):
    c = QFrame(); c.setObjectName("Card")
    c.setStyleSheet(f"QFrame#Card {{background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 rgba(16,27,50,0.86),stop:0.55 rgba(10,16,32,0.86),stop:1 rgba(21,38,75,0.82)); border:1px solid #263D69; border-radius:22px;}}")
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
        # Scope transparent typography and dark glass surfaces to this page.
        self.setObjectName("AdminContentPage")
        self.setStyleSheet("""
            QWidget#AdminContentPage { background: transparent; }
            QWidget#AdminContentPage QLabel { background: transparent; border: none; }
            QWidget#AdminContentPage QTableWidget {
                background: rgba(10, 16, 32, 0.86);
                border: 1px solid #263D69;
                border-radius: 18px;
                gridline-color: transparent;
                selection-background-color: #15264B;
            }
            QWidget#AdminContentPage QHeaderView::section {
                background: #101B32;
                color: #82B1FF;
                padding: 12px 8px;
                border: none;
                border-bottom: 1px solid #263D69;
                font-weight: 700;
            }
            QWidget#AdminContentPage QTableWidget::item {
                padding: 6px 8px;
                border-bottom: 1px solid #15264B;
            }
        """)

        v = QVBoxLayout(self); v.setContentsMargins(24,24,24,22); v.setSpacing(16)

        head = QLabel("Dashboard")
        head.setStyleSheet(f"color:{TEXT}; font-family: Segoe UI Variable; font-size:30px; font-weight:800;")
        v.addWidget(head)
        sub = QLabel("Overview of kiosk activity")
        sub.setStyleSheet(f"color:{TEXT_MUTED}; font-size:14px;")
        v.addWidget(sub)

        from backend.services.admin_service import AdminService
        admin_service = AdminService()
        sync_stats = admin_service.get_dashboard_stats()
        
        grid = QGridLayout(); grid.setSpacing(14)
        grid.addWidget(stat_card("Total Questions", str(sync_stats.get('total_questions', 0)), "▲ Overall Volume", ACCENT_HI), 0, 0)
        grid.addWidget(stat_card("Answered Questions", str(sync_stats.get('answered_questions', 0)), "▲ System Served", SUCCESS), 0, 1)
        grid.addWidget(stat_card("Unanswered Questions", str(sync_stats.get('unanswered_questions', 0)), "▼ Pending Review", WARNING), 0, 2)
        grid.addWidget(stat_card("Flagged Responses", str(sync_stats.get('flagged_responses', 0)), "▼ Unhelpful", "#ff4d4f"), 0, 3)
        v.addLayout(grid)

        # Most asked
        wrap = QFrame(); wrap.setObjectName("Card")
        wrap.setStyleSheet(f"QFrame#Card {{background:rgba(16,27,50,0.91); border:1px solid #263D69; border-radius:20px;}}")
        wv = QVBoxLayout(wrap); wv.setContentsMargins(22,18,22,18); wv.setSpacing(10)
        wt = QLabel("Most Asked Questions")
        wt.setStyleSheet(f"color:{TEXT}; font-size:18px; font-weight:700;")
        wv.addWidget(wt)
        
        from backend.services.dashboard_service import DashboardService
        most_asked = DashboardService().get_most_asked(limit=5)
        if not most_asked:
            most_asked = [("No questions recorded yet.", 0)]
            
        for q, n in most_asked:
            row = QFrame(); row.setObjectName("Card")
            row.setStyleSheet("QFrame#Card {background:rgba(10,16,32,0.86); border:1px solid #263D69; border-radius:14px;}")
            h = QHBoxLayout(row); h.setContentsMargins(16,10,16,10)
            qq = QLabel(str(q)); qq.setWordWrap(True); qq.setMinimumHeight(44)
            qq.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            qq.setStyleSheet(f"color:{TEXT}; font-size:15px; background:transparent; border:none;")
            count = QLabel(f"{n} asks")
            count.setStyleSheet(f"color:{ACCENT_HI}; background:#15264B;"
                                f"border-radius:10px; padding:4px 10px; font-size:12px; font-weight:700;")
            h.addWidget(qq, 1); h.addWidget(count)
            wv.addWidget(row)
        v.addWidget(wrap, 0)
        v.addStretch(1)
