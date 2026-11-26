"""Pending Reviews management page."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                             QAbstractItemView, QMessageBox, QDialog, QTextEdit)
from theme import TEXT, TEXT_MUTED, SUCCESS, DANGER, WARNING, PANEL_HI, BORDER
from admin.glass import ADMIN_QSS, SURFACE, ROW, EDGE, badge, glass_button, set_cell, GlassDialog, confirm
from backend.services.admin_service import AdminService

class CorrectDialog(GlassDialog):
    def __init__(self, parent=None, scheme_name=""):
        super().__init__(parent, "Correct Scheme Information", "Review and update missing eligibility details before publishing.", 680)
        self.resize(680, 390)
        v = self.body
        v.addWidget(QLabel(f"Provide missing eligibility for:\n{scheme_name}"))
        self.te = QTextEdit()
        self.te.setPlaceholderText("Enter verified eligibility information...")
        v.addWidget(self.te)
        
        acts = QHBoxLayout()
        acts.addStretch(1)
        cancel = glass_button("Cancel")
        cancel.clicked.connect(self.reject)
        acts.addWidget(cancel)
        save = glass_button("Save Correction", "green"); save.clicked.connect(self.accept)
        acts.addWidget(save)
        v.addLayout(acts)

    def get_text(self):
        return self.te.toPlainText().strip()


class PendingReviewsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Scope transparent typography and dark glass surfaces to this page.
        self.setObjectName("AdminContentPage")
        self.setStyleSheet(ADMIN_QSS)

        self.service = AdminService()
        self.v = QVBoxLayout(self); self.v.setContentsMargins(24,18,24,20); self.v.setSpacing(12)

        head = QLabel("Verify Imported Information")
        head.setStyleSheet(f"color:{TEXT}; font-size:26px; font-weight:800;")
        self.v.addWidget(head)
        sub = QLabel("Legacy information is quarantined. Publication requires official evidence and a complete verified revision.")
        sub.setStyleSheet(f"color:{TEXT_MUTED}; font-size:14px;")
        self.v.addWidget(sub)

        self.table = QTableWidget()
        self.v.addWidget(self.table, 1)
        self.refresh_data()

    def refresh_data(self):
        self.data_list = self.service.get_pending_reviews()
        self.table.clear()
        self.table.clearSpans()
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
        h.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(3, 158)
        h.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(4, 322)

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
            set_cell(self.table, r, 3, badge(status, "amber"))
            
            btn_app = glass_button("✓ Approve", "green")
            btn_app.setEnabled(False)
            btn_app.setToolTip("Publication is paused until the evidence-based editor is ready.")
            
            btn_cor = glass_button("Correct", "amber")
            btn_cor.setEnabled(False)
            btn_cor.setToolTip("Legacy records cannot be published by editing eligibility alone.")
            
            btn_rej = glass_button("✗ Reject", "red")
            btn_rej.clicked.connect(lambda _, rid=rev_id, sid=sch_id: self._handle_action(rid, sid, "Reject"))
            
            set_cell(self.table, r, 4, btn_app, btn_cor, btn_rej)

    def _show_toast(self, msg, level="success"):
        if hasattr(self.window(), "show_toast"):
            self.window().show_toast(msg, level)

    def _handle_action(self, review_id, scheme_id, action, name=""):
        corrected_text = None
        if action in ("Approve", "Reject"):
            if not confirm(self, f"{action} Information", f"Are you sure you want to {action.lower()} this imported information?", action, "green" if action == "Approve" else "red"):
                return
        if action == "Correct":
            dlg = CorrectDialog(self, name)
            if dlg.exec() == QDialog.DialogCode.Accepted:
                corrected_text = dlg.get_text()
                if not corrected_text:
                    QMessageBox.warning(self, "Error", "Eligibility cannot be empty.")
                    return
            else:
                return

        # Attempt to get user_id from parent Shell
        user_id = None
        if hasattr(self.window(), "user_session") and self.window().user_session:
            user_id = self.window().user_session.get("id")

        if self.service.update_review_status(review_id, scheme_id, action, corrected_text, user_id=user_id):
            self.refresh_data()
            self._show_toast("Review rejected. Original record retained.", "success")
        else:
            QMessageBox.warning(self, "Review not changed", "Legacy publication is disabled or the migration is not installed.")
