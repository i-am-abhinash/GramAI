"""Sync Logs view page."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QAbstractItemView)
from theme import TEXT, TEXT_MUTED
from backend.services.admin_service import AdminService

class SyncLogsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.service = AdminService()
        self.v = QVBoxLayout(self); self.v.setContentsMargins(30,28,30,28); self.v.setSpacing(16)

        head = QLabel("Automated Sync Logs")
        head.setStyleSheet(f"color:{TEXT}; font-size:26px; font-weight:800;")
        self.v.addWidget(head)
        sub = QLabel("Historical logs of the Automated Scheme Sync Engine.")
        sub.setStyleSheet(f"color:{TEXT_MUTED}; font-size:14px;")
        self.v.addWidget(sub)

        self.table = QTableWidget()
        self.v.addWidget(self.table, 1)
        self._load_data()

    def _load_data(self):
        data_list = self.service.get_sync_logs(limit=100)
        self.table.clear()
        self.table.setRowCount(len(data_list))
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Sync Time", "Status", "Imported", "Updated", "Failed"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setDefaultSectionSize(50)
        
        h = self.table.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        h.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        h.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        h.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        h.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        for r, item in enumerate(data_list):
            sync_time = str(item['sync_time'])[:19]
            status = str(item['status'])
            imp = str(item.get('records_imported', 0))
            upd = str(item.get('records_updated', 0))
            fail = str(item.get('failed_imports', 0))
            
            self.table.setItem(r, 0, QTableWidgetItem("  " + sync_time))
            self.table.setItem(r, 1, QTableWidgetItem("  " + status))
            self.table.setItem(r, 2, QTableWidgetItem("  " + imp))
            self.table.setItem(r, 3, QTableWidgetItem("  " + upd))
            self.table.setItem(r, 4, QTableWidgetItem("  " + fail))
