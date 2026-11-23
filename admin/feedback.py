"""Feedback Review management page."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
                             QTableWidgetItem, QHeaderView, QAbstractItemView, QComboBox)
from theme import TEXT, TEXT_MUTED, SUCCESS, DANGER

class FeedbackPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Scope transparent typography and dark glass surfaces to this page.
        self.setObjectName("AdminContentPage")
        self.setStyleSheet("""
            QWidget#AdminContentPage { background: transparent; }
            QWidget#AdminContentPage QLabel { background: transparent; border: none; }
            QWidget#AdminContentPage QTableWidget {
                background: rgba(10, 26, 49, 0.86);
                border: 1px solid #36688C;
                border-radius: 18px;
                gridline-color: transparent;
                selection-background-color: #183F68;
            }
            QWidget#AdminContentPage QHeaderView::section {
                background: #172E4C;
                color: #BFE6FF;
                padding: 12px 8px;
                border: none;
                border-bottom: 1px solid #315A7C;
                font-weight: 700;
            }
            QWidget#AdminContentPage QTableWidget::item {
                padding: 6px 8px;
                border-bottom: 1px solid #1D3553;
            }
        """)

        self.v = QVBoxLayout(self); self.v.setContentsMargins(30,28,30,28); self.v.setSpacing(16)

        head = QLabel("Feedback & Response Review")
        head.setStyleSheet(f"color:{TEXT}; font-size:26px; font-weight:800;")
        self.v.addWidget(head)
        sub = QLabel("Monitor citizen feedback to ensure GramAI is providing accurate, helpful information.")
        sub.setStyleSheet(f"color:{TEXT_MUTED}; font-size:14px;")
        self.v.addWidget(sub)

        # Filters
        bar = QHBoxLayout(); bar.setSpacing(10)
        self.filter_cb = QComboBox()
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
        h.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        h.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        self.feedback_data = data
        for r, item in enumerate(data):
            self.table.setItem(r, 0, QTableWidgetItem("  " + str(item.get('query', ''))))
            self.table.setItem(r, 1, QTableWidgetItem("  " + str(item.get('response', ''))))
            
            fb = str(item.get('status', 'Helpful'))
            color = SUCCESS if fb == "Helpful" else DANGER
            chip = QLabel(fb)
            chip.setStyleSheet(f"color:{color}; background: rgba(255,255,255,15); border-radius:10px; padding:4px 10px; font-size:12px; font-weight:700;")
            chip_wrap = QWidget(); cw = QHBoxLayout(chip_wrap); cw.setContentsMargins(8,0,8,0); cw.addWidget(chip); cw.addStretch(1)
            self.table.setCellWidget(r, 2, chip_wrap)
            
            self.table.setItem(r, 3, QTableWidgetItem("  " + str(item.get('date', '2026-06-07'))[:10]))

    def _filter_rows(self, index):
        for row, item in enumerate(self.feedback_data):
            status = item.get("status", "")
            visible = index == 0 or (index == 1 and status == "Helpful") or (index == 2 and status in ("Unhelpful", "Flagged"))
            self.table.setRowHidden(row, not visible)
