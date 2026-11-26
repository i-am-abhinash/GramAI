"""Imported Government Schemes view page."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                             QAbstractItemView, QComboBox, QMessageBox)
from theme import PANEL, PANEL_HI, ACCENT_HI, BORDER, TEXT, TEXT_MUTED, SUCCESS
from admin.glass import ADMIN_QSS, SURFACE, ROW, EDGE, badge, glass_button, set_cell, GlassDialog, confirm
from backend.services.admin_service import AdminService

class SchemesPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Scope transparent typography and dark glass surfaces to this page.
        self.setObjectName("AdminContentPage")
        self.setStyleSheet(ADMIN_QSS)

        self.service = AdminService()
        self.v = QVBoxLayout(self); self.v.setContentsMargins(24,18,24,20); self.v.setSpacing(12)

        head_row = QHBoxLayout()
        head = QLabel("Imported Government Schemes")
        head.setStyleSheet(f"color:{TEXT}; font-size:26px; font-weight:800;")
        head_row.addWidget(head); head_row.addStretch(1)
        sync_btn = glass_button("↻ Run Manual Sync")
        sync_btn.setMinimumHeight(42)
        sync_btn.setEnabled(False)
        sync_btn.setToolTip("Mock sync disabled. Official-source adapters are not ready.")
        head_row.addWidget(sync_btn)
        self.v.addLayout(head_row)

        sub = QLabel("Legacy scheme records (unverified). Citizen answers use a separate verified knowledge base.")
        sub.setStyleSheet(f"color:{TEXT_MUTED}; font-size:14px;")
        self.v.addWidget(sub)

        bar = QHBoxLayout(); bar.setSpacing(10)
        self.search = QLineEdit(); self.search.setPlaceholderText("🔍  Search schemes…"); self.search.setMinimumHeight(42)
        
        # Debounced search timer
        from PyQt6.QtCore import QTimer
        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(300)
        self._search_timer.timeout.connect(self._filter)
        self.search.textChanged.connect(lambda: self._search_timer.start())
        
        bar.addWidget(self.search, 1)
        
        self.cat_filter = QComboBox()
        self.cat_filter.addItems(["All Categories", "Agriculture", "Education", "Health", "Housing", "Pension", "Welfare", "Other"])
        self.cat_filter.setMinimumHeight(42)
        self.cat_filter.setMinimumWidth(180)
        self.cat_filter.currentTextChanged.connect(self._filter)
        bar.addWidget(self.cat_filter)
        
        self.v.addLayout(bar)

        self.table = QTableWidget()
        self.v.addWidget(self.table, 1)
        self.refresh_data()

    def _show_toast(self, msg, level="success"):
        if hasattr(self.window(), "show_toast"):
            self.window().show_toast(msg, level)

    def _trigger_sync(self):
        result = self.service.trigger_sync()
        if result.get("success"):
            self._show_toast(f"Sync complete. Imported: {result['imported']}, Updated: {result['updated']}", "success")
            self.refresh_data()
        else:
            self._show_toast(f"Sync failed: {result.get('error')}", "error")

    def refresh_data(self):
        self.schemes_data = self.service.get_imported_schemes()
        self._filter()

    def _filter(self):
        txt = self.search.text().lower()
        cat = self.cat_filter.currentText()
        filtered = []
        for s in self.schemes_data:
            match_txt = txt in str(s['name']).lower() or txt in str(s['description']).lower()
            match_cat = cat == "All Categories" or str(s.get('category')) == cat
            if match_txt and match_cat:
                filtered.append(s)
        self._populate_table(filtered)

    def _populate_table(self, data_list):
        self.table.clear()
        self.table.clearSpans()
        self.table.setRowCount(len(data_list))
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Name", "Category", "Description", "Source", "Last Sync"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setDefaultSectionSize(70)
        h = self.table.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(0, 220)
        h.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        h.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        h.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        h.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        self.table.setWordWrap(True)
        self.table.setTextElideMode(Qt.TextElideMode.ElideRight)
        if not data_list:
            self.table.setRowCount(1)
            self.table.setSpan(0, 0, 1, 5)
            empty = QTableWidgetItem("No schemes match your filters. Try another search or category.")
            empty.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(0, 0, empty)
            return
        for r, s in enumerate(data_list):
            name = str(s['name'])
            cat = str(s.get('category') or 'Welfare')
            desc = str(s.get('description') or '')
            source = str(s.get('source_name') or 'Unknown')
            sync_date = str(s.get('last_sync_date', ''))[:16]
            if len(desc) > 120: desc = desc[:117] + "..."
            
            self.table.setItem(r, 0, QTableWidgetItem("  " + name))
            self.table.setItem(r, 1, QTableWidgetItem("  " + cat))
            self.table.setItem(r, 2, QTableWidgetItem("  " + desc))
            self.table.setItem(r, 3, QTableWidgetItem("  " + source))
            self.table.setItem(r, 4, QTableWidgetItem("  " + sync_date))
