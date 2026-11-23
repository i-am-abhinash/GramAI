"""Pending Reviews management page."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                             QAbstractItemView, QMessageBox, QDialog, QTextEdit)
from theme import TEXT, TEXT_MUTED, SUCCESS, DANGER, WARNING, PANEL_HI, BORDER
from backend.services.admin_service import AdminService

class CorrectDialog(QDialog):
    def __init__(self, parent=None, scheme_name=""):
        super().__init__(parent)
        self.setWindowTitle("Correct Scheme Info")
        self.setFixedSize(500, 300)
        v = QVBoxLayout(self)
        v.addWidget(QLabel(f"Provide missing eligibility for:\n{scheme_name}"))
        self.te = QTextEdit()
        self.te.setStyleSheet(f"background: {PANEL_HI}; border: 1px solid {BORDER};")
        v.addWidget(self.te)
        
        acts = QHBoxLayout()
        acts.addStretch(1)
        save = QPushButton("Save Correction"); save.clicked.connect(self.accept)
        save.setStyleSheet(f"background: {SUCCESS}; color: white; padding: 6px 12px; border-radius: 6px;")
        acts.addWidget(save)
        v.addLayout(acts)

    def get_text(self):
        return self.te.toPlainText().strip()


class PendingReviewsPage(QWidget):
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

        head = QLabel("Verify Imported Information")
        head.setStyleSheet(f"color:{TEXT}; font-size:26px; font-weight:800;")
        self.v.addWidget(head)
        sub = QLabel("Review automatically acquired government information before it is published.")
        sub.setStyleSheet(f"color:{TEXT_MUTED}; font-size:14px;")
        self.v.addWidget(sub)

        self.table = QTableWidget()
        self.v.addWidget(self.table, 1)
        self._load_data()

    def _load_data(self):
        self.data_list = self.service.get_pending_reviews()
        self.table.clear()
        self.table.setRowCount(len(self.data_list))
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Scheme Name", "Information Source", "Imported Date", "Status", "Actions"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setDefaultSectionSize(76)
        
        h = self.table.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        h.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        h.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        h.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        h.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(4, 280)

        self.table.setWordWrap(True)
        self.table.setTextElideMode(Qt.TextElideMode.ElideMiddle)
        if not self.data_list:
            self.table.setRowCount(1)
            self.table.setSpan(0, 0, 1, 5)
            empty = QTableWidgetItem("✓  No pending information to verify. New imports will appear here.")
            empty.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(0, 0, empty)
            self.table.verticalHeader().setDefaultSectionSize(100)
            return

        for r, item in enumerate(self.data_list):
            rev_id = item['review_id']
            sch_id = item['scheme_id']
            name = str(item['name'])
            
            # Formulate source
            source_url = str(item.get('source_url', 'Unknown'))
            
            # Get date from created_at
            imported_date = str(item.get('created_at', ''))[:10]
            status = str(item.get('status', 'Pending Review'))
            
            self.table.setItem(r, 0, QTableWidgetItem("  " + name))
            self.table.setItem(r, 1, QTableWidgetItem("  " + source_url))
            self.table.setItem(r, 2, QTableWidgetItem("  " + imported_date))
            self.table.setItem(r, 3, QTableWidgetItem("  " + status))
            
            actions = QHBoxLayout(); actions.setContentsMargins(4,4,4,4); actions.setSpacing(4)
            
            btn_app = QPushButton("✓ Approve")
            btn_app.setStyleSheet(f"background: {SUCCESS}; color: white; padding: 4px; border-radius: 4px;")
            btn_app.clicked.connect(lambda _, rid=rev_id, sid=sch_id: self._handle_action(rid, sid, "Approve"))
            
            btn_cor = QPushButton("✏️ Correct")
            btn_cor.setStyleSheet(f"background: {WARNING}; color: white; padding: 4px; border-radius: 4px;")
            btn_cor.clicked.connect(lambda _, rid=rev_id, sid=sch_id, nm=name: self._handle_action(rid, sid, "Correct", nm))
            
            btn_rej = QPushButton("✗ Reject")
            btn_rej.setStyleSheet(f"background: {DANGER}; color: white; padding: 4px; border-radius: 4px;")
            btn_rej.clicked.connect(lambda _, rid=rev_id, sid=sch_id: self._handle_action(rid, sid, "Reject"))
            
            actions.addWidget(btn_app)
            actions.addWidget(btn_cor)
            actions.addWidget(btn_rej)
            
            w = QWidget(); w.setLayout(actions)
            self.table.setCellWidget(r, 4, w)

    def _handle_action(self, review_id, scheme_id, action, name=""):
        corrected_text = None
        if action == "Correct":
            dlg = CorrectDialog(self, name)
            if dlg.exec() == QDialog.DialogCode.Accepted:
                corrected_text = dlg.get_text()
                if not corrected_text:
                    QMessageBox.warning(self, "Error", "Eligibility cannot be empty.")
                    return
            else:
                return

        self.service.update_review_status(review_id, scheme_id, action, corrected_text)
        self._load_data()
