"""Query Logs page."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QAbstractItemView)
from theme import PANEL, BORDER, TEXT, TEXT_MUTED, SUCCESS, WARNING

class QueryLogsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        v = QVBoxLayout(self); v.setContentsMargins(30,28,30,28); v.setSpacing(16)

        head_row = QHBoxLayout()
        head = QLabel("Query Logs")
        head.setStyleSheet(f"color:{TEXT}; font-size:26px; font-weight:800;")
        head_row.addWidget(head); head_row.addStretch(1)
        export = QPushButton("⬇ Export CSV"); export.setObjectName("Ghost"); export.setMinimumHeight(42)
        head_row.addWidget(export)
        v.addLayout(head_row)

        sub = QLabel("Full audit log of every question asked at the kiosk.")
        sub.setStyleSheet(f"color:{TEXT_MUTED}; font-size:14px;")
        v.addWidget(sub)

        # Toolbar
        bar = QHBoxLayout(); bar.setSpacing(10)
        search = QLineEdit(); search.setPlaceholderText("🔍  Search logs by question or response…"); search.setMinimumHeight(42)
        bar.addWidget(search, 1)
        v.addLayout(bar)

        from backend.services.admin_service import AdminService
        self.service = AdminService()
        self.logs_data = self.service.get_query_logs()
        
        # Table
        table = QTableWidget(len(self.logs_data), 4)
        table.setHorizontalHeaderLabels(["Timestamp", "Question", "Response", "Status"])
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setShowGrid(False)
        table.verticalHeader().setDefaultSectionSize(48)
        h = table.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        h.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        h.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        h.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        for r, log in enumerate(self.logs_data):
            time_str = str(log['created_at'])
            q_text = str(log['query_text'])
            a_text = str(log['response_text'])
            if len(a_text) > 50:
                a_text = a_text[:47] + "..."
            
            is_successful = log['is_successful']

            table.setItem(r, 0, QTableWidgetItem("  " + time_str))
            table.setItem(r, 1, QTableWidgetItem("  " + q_text))
            table.setItem(r, 2, QTableWidgetItem("  " + a_text))

            status_str = "Matched" if is_successful else "Unanswered"
            color = SUCCESS if is_successful else WARNING
            
            chip = QLabel(status_str)
            chip.setStyleSheet(
                f"color:{color}; background: rgba(255,255,255,15); "
                f"border-radius:10px; padding:4px 10px; font-size:11px; font-weight:700;"
            )
            chip_wrap = QWidget(); cw = QHBoxLayout(chip_wrap); cw.setContentsMargins(8,0,8,0); cw.addWidget(chip); cw.addStretch(1)
            table.setCellWidget(r, 3, chip_wrap)

        v.addWidget(table, 1)
