"""Query Logs page."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QAbstractItemView)
from theme import PANEL, BORDER, TEXT, TEXT_MUTED, SUCCESS, WARNING

import csv
from backend.services.admin_service import AdminService
from PyQt6.QtWidgets import QFileDialog, QMessageBox

class QueryLogsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.service = AdminService()
        self.logs_data = []
        self.filtered_data = []
        
        self.v = QVBoxLayout(self); self.v.setContentsMargins(30,28,30,28); self.v.setSpacing(16)

        head_row = QHBoxLayout()
        head = QLabel("Query Logs")
        head.setStyleSheet(f"color:{TEXT}; font-size:26px; font-weight:800;")
        head_row.addWidget(head); head_row.addStretch(1)
        export = QPushButton("⬇ Export CSV"); export.setObjectName("Ghost"); export.setMinimumHeight(42)
        export.clicked.connect(self._export_csv)
        head_row.addWidget(export)
        self.v.addLayout(head_row)

        sub = QLabel("Full audit log of every question asked at the kiosk.")
        sub.setStyleSheet(f"color:{TEXT_MUTED}; font-size:14px;")
        self.v.addWidget(sub)

        # Toolbar
        bar = QHBoxLayout(); bar.setSpacing(10)
        self.search = QLineEdit(); self.search.setPlaceholderText("🔍  Search logs by question or response…"); self.search.setMinimumHeight(42)
        
        # Debounced search timer
        from PyQt6.QtCore import QTimer
        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(300)
        self._search_timer.timeout.connect(self._apply_filter)
        self.search.textChanged.connect(lambda: self._search_timer.start())
        
        bar.addWidget(self.search, 1)
        self.v.addLayout(bar)

        self.table = QTableWidget()
        self.v.addWidget(self.table, 1)
        self.refresh_data()

    def refresh_data(self):
        self.logs_data = self.service.get_query_logs()
        self._apply_filter()

    def _apply_filter(self):
        query = self.search.text().lower().strip()
        if not query:
            self.filtered_data = self.logs_data
        else:
            self.filtered_data = [
                log for log in self.logs_data 
                if query in str(log.get('query_text', '')).lower() or query in str(log.get('response_text', '')).lower()
            ]
        self._render_table()

    def _render_table(self):
        self.table.clear()
        self.table.setRowCount(len(self.filtered_data))
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Timestamp", "Question", "Response", "Status"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setDefaultSectionSize(48)
        h = self.table.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        h.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        h.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        h.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        for r, log in enumerate(self.filtered_data):
            time_str = str(log['created_at'])
            q_text = str(log['query_text'])
            a_text = str(log['response_text'])
            if len(a_text) > 50:
                a_text = a_text[:47] + "..."
            
            is_successful = log['is_successful']

            self.table.setItem(r, 0, QTableWidgetItem("  " + time_str))
            self.table.setItem(r, 1, QTableWidgetItem("  " + q_text))
            self.table.setItem(r, 2, QTableWidgetItem("  " + a_text))

            status_str = "Matched" if is_successful else "Unanswered"
            color = SUCCESS if is_successful else WARNING
            
            chip = QLabel(status_str)
            chip.setStyleSheet(
                f"color:{color}; background: rgba(255,255,255,15); "
                f"border-radius:10px; padding:4px 10px; font-size:11px; font-weight:700;"
            )
            chip_wrap = QWidget(); cw = QHBoxLayout(chip_wrap); cw.setContentsMargins(8,0,8,0); cw.addWidget(chip); cw.addStretch(1)
            self.table.setCellWidget(r, 3, chip_wrap)

    def _show_toast(self, msg, level="success"):
        if hasattr(self.window(), "show_toast"):
            self.window().show_toast(msg, level)

    def _export_csv(self):
        if not self.filtered_data:
            self._show_toast("No data to export", "warning")
            return
            
        filename, _ = QFileDialog.getSaveFileName(self, "Save Query Logs", "query_logs.csv", "CSV Files (*.csv);;All Files (*)")
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Timestamp", "Question", "Response", "Status"])
                    for log in self.filtered_data:
                        writer.writerow([
                            str(log['created_at']),
                            str(log['query_text']),
                            str(log['response_text']),
                            "Matched" if log['is_successful'] else "Unanswered"
                        ])
                self._show_toast(f"Exported to {filename}", "success")
            except Exception as e:
                self._show_toast(f"Export failed: {e}", "error")
