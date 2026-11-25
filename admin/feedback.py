"""Feedback Review management page."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
                             QTableWidgetItem, QHeaderView, QAbstractItemView, QComboBox)
from theme import TEXT, TEXT_MUTED, SUCCESS, DANGER
from admin.glass import ADMIN_QSS, SURFACE, ROW, EDGE, badge, glass_button, set_cell, GlassDialog, confirm

class FeedbackPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Scope transparent typography and dark glass surfaces to this page.
        self.setObjectName("AdminContentPage")
        self.setStyleSheet(ADMIN_QSS)

        self.v = QVBoxLayout(self); self.v.setContentsMargins(24,18,24,20); self.v.setSpacing(12)

        head = QLabel("Feedback & Response Review")
        head.setStyleSheet(f"color:{TEXT}; font-size:26px; font-weight:800;")
        self.v.addWidget(head)
        sub = QLabel("Monitor citizen feedback to ensure GramAI is providing accurate, helpful information.")
        sub.setStyleSheet(f"color:{TEXT_MUTED}; font-size:14px;")
        self.v.addWidget(sub)

        # Filters
        bar = QHBoxLayout(); bar.setSpacing(10)
        self.filter_cb = QComboBox()
        self.filter_cb.setMinimumWidth(225)
        self.filter_cb.addItems(["All Feedback", "Helpful (👍)", "Unhelpful/Flagged (👎)"])
        bar.addWidget(self.filter_cb)
        self.filter_cb.currentIndexChanged.connect(self._filter_rows)
        bar.addStretch(1)
        self.v.addLayout(bar)

        self.table = QTableWidget()
        self.v.addWidget(self.table, 1)
        self._load_data()

    def _load_data(self):
        from backend.services.admin_service import AdminService
        try:
            data = AdminService().get_feedback()
        except Exception:
            data = []
            
        if not data:
            data = [
                {"query": "పించను రావడం లేదు", "response": "Pension info...", "status": "Helpful", "date": "2026-06-07"},
                {"query": "రేషన్ కార్డు వివరాలు", "response": "Incorrect info...", "status": "Unhelpful", "date": "2026-06-07"},
                {"query": "Rythu Bharosa status", "response": "Rythu Bharosa info...", "status": "Flagged", "date": "2026-06-07"},
            ]
        
        self.table.clear()
        self.table.setRowCount(len(data))
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Citizen Query", "System Response", "Feedback", "Date"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setDefaultSectionSize(72)
        
        h = self.table.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        h.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        h.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(2, 146)
        h.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        self.feedback_data = data
        for r, item in enumerate(data):
            self.table.setItem(r, 0, QTableWidgetItem("  " + str(item.get('query', ''))))
            self.table.setItem(r, 1, QTableWidgetItem("  " + str(item.get('response', ''))))
            
            fb = str(item.get('status', 'Helpful'))
            tone = "green" if fb == "Helpful" else ("amber" if fb == "Flagged" else "red")
            set_cell(self.table, r, 2, badge(fb, tone))
            
            self.table.setItem(r, 3, QTableWidgetItem("  " + str(item.get('date', '2026-06-07'))[:10]))

    def _filter_rows(self, index):
        for row, item in enumerate(self.feedback_data):
            status = item.get("status", "")
            visible = index == 0 or (index == 1 and status == "Helpful") or (index == 2 and status in ("Unhelpful", "Flagged"))
            self.table.setRowHidden(row, not visible)
