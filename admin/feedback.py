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
        # Mocking data until actual DB integration is hooked up
        mock_data = [
            {"query": "పించను రావడం లేదు", "response": "Pension info...", "status": "Helpful"},
            {"query": "రేషన్ కార్డు వివరాలు", "response": "Incorrect info...", "status": "Unhelpful"},
            {"query": "Rythu Bharosa status", "response": "Rythu Bharosa info...", "status": "Flagged"},
        ]
        
        self.table.clear()
        self.table.setRowCount(len(mock_data))
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

        self.feedback_data = mock_data
        for r, item in enumerate(mock_data):
            self.table.setItem(r, 0, QTableWidgetItem("  " + item['query']))
            self.table.setItem(r, 1, QTableWidgetItem("  " + item['response']))
            
            fb = item['status']
            color = SUCCESS if fb == "Helpful" else DANGER
            chip = QLabel(fb)
            chip.setStyleSheet(f"color:{color}; background: rgba(255,255,255,15); border-radius:10px; padding:4px 10px; font-size:12px; font-weight:700;")
            chip_wrap = QWidget(); cw = QHBoxLayout(chip_wrap); cw.setContentsMargins(8,0,8,0); cw.addWidget(chip); cw.addStretch(1)
            self.table.setCellWidget(r, 2, chip_wrap)
            
            self.table.setItem(r, 3, QTableWidgetItem("  2026-06-07"))

    def _filter_rows(self, index):
        for row, item in enumerate(self.feedback_data):
            status = item["status"]
            visible = index == 0 or (index == 1 and status == "Helpful") or (index == 2 and status in ("Unhelpful", "Flagged"))
            self.table.setRowHidden(row, not visible)
