"""Imported Government Schemes view page."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                             QAbstractItemView, QComboBox, QMessageBox)
from theme import PANEL, PANEL_HI, ACCENT_HI, BORDER, TEXT, TEXT_MUTED, SUCCESS
from backend.services.admin_service import AdminService

class SchemesPage(QWidget):
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

        self.service = AdminService()
        self.v = QVBoxLayout(self); self.v.setContentsMargins(30,28,30,28); self.v.setSpacing(16)

        head_row = QHBoxLayout()
        head = QLabel("Imported Government Schemes")
        head.setStyleSheet(f"color:{TEXT}; font-size:26px; font-weight:800;")
        head_row.addWidget(head); head_row.addStretch(1)
        sync_btn = QPushButton("🔄 Run Manual Sync")
        sync_btn.setObjectName("Primary"); sync_btn.setMinimumHeight(42)
        sync_btn.clicked.connect(self._trigger_sync)
        head_row.addWidget(sync_btn)
        self.v.addLayout(head_row)

        sub = QLabel("Read-only view of government welfare schemes synchronized from official portals.")
        sub.setStyleSheet(f"color:{TEXT_MUTED}; font-size:14px;")
        self.v.addWidget(sub)

        bar = QHBoxLayout(); bar.setSpacing(10)
        self.search = QLineEdit(); self.search.setPlaceholderText("🔍  Search schemes…"); self.search.setMinimumHeight(42)
        self.search.textChanged.connect(self._filter)
        bar.addWidget(self.search, 1)
        
        self.cat_filter = QComboBox()
        self.cat_filter.addItems(["All Categories", "Agriculture", "Education", "Health", "Housing", "Pension", "Welfare", "Other"])
        self.cat_filter.setMinimumHeight(42)
        self.cat_filter.currentTextChanged.connect(self._filter)
        bar.addWidget(self.cat_filter)
        
        self.v.addLayout(bar)

        self.table = QTableWidget()
        self.v.addWidget(self.table, 1)
        self._load_data()

    def _trigger_sync(self):
        result = self.service.trigger_sync()
        if result.get("success"):
            QMessageBox.information(self, "Sync Complete", f"Successfully synced.\nImported: {result['imported']}\nUpdated: {result['updated']}")
            self._load_data()
        else:
            QMessageBox.warning(self, "Sync Failed", f"Sync failed: {result.get('error')}")

    def _load_data(self):
        self.schemes_data = self.service.get_imported_schemes()
        self._populate_table(self.schemes_data)

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
