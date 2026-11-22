"""Feedback Review management page."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
                             QTableWidgetItem, QHeaderView, QAbstractItemView, QComboBox)
from theme import TEXT, TEXT_MUTED, SUCCESS, DANGER

class FeedbackPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
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
        self.filter_cb.currentTextChanged.connect(self._filter)
        bar.addWidget(self.filter_cb)
        bar.addStretch(1)
        self.v.addLayout(bar)

        self.table = QTableWidget()
        self.v.addWidget(self.table, 1)
        self.refresh_data()

    def refresh_data(self):
        # Mocking data until actual DB integration is hooked up
        self.mock_data = [
            {"query": "పించను రావడం లేదు", "response": "Pension info...", "status": "Helpful"},
            {"query": "రేషన్ కార్డు వివరాలు", "response": "Incorrect info...", "status": "Unhelpful"},
            {"query": "Rythu Bharosa status", "response": "Rythu Bharosa info...", "status": "Flagged"},
        ]
        self._filter()

    def _filter(self):
        cat = self.filter_cb.currentText()
        filtered = []
        for item in self.mock_data:
            st = item['status']
            if cat == "All Feedback":
                filtered.append(item)
            elif cat == "Helpful (👍)" and st == "Helpful":
                filtered.append(item)
            elif cat == "Unhelpful/Flagged (👎)" and st in ["Unhelpful", "Flagged"]:
                filtered.append(item)
        self._render_table(filtered)

    def _render_table(self, data):
        self.table.clear()
        self.table.setRowCount(len(data))
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Citizen Query", "System Response", "Feedback", "Date"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setDefaultSectionSize(60)
        
        h = self.table.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        h.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        h.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        h.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        for r, item in enumerate(data):
            self.table.setItem(r, 0, QTableWidgetItem("  " + item['query']))
            self.table.setItem(r, 1, QTableWidgetItem("  " + item['response']))
            
            fb = item['status']
            color = SUCCESS if fb == "Helpful" else DANGER
            chip = QLabel(fb)
            chip.setStyleSheet(f"color:{color}; background: rgba(255,255,255,15); border-radius:10px; padding:4px 10px; font-size:12px; font-weight:700;")
            chip_wrap = QWidget(); cw = QHBoxLayout(chip_wrap); cw.setContentsMargins(8,0,8,0); cw.addWidget(chip); cw.addStretch(1)
            self.table.setCellWidget(r, 2, chip_wrap)
            
            self.table.setItem(r, 3, QTableWidgetItem("  2026-06-07"))
