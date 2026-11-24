"""Unanswered Questions management page."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QAbstractItemView, QFrame, QDialog, QTextEdit, QMessageBox, QComboBox)
from theme import PANEL, PANEL_HI, ACCENT_HI, BORDER, TEXT, TEXT_MUTED, WARNING, SUCCESS
from backend.services.admin_service import AdminService

class ReviewDialog(QDialog):
    def __init__(self, parent=None, query_id=None, q_text="", current_status="Pending"):
        super().__init__(parent)
        self.query_id = query_id
        self.q_text = q_text
        self.setWindowTitle("Review & Create Response")
        self.setFixedSize(600, 500)
        self.setStyleSheet(f"background: {PANEL}; color: {TEXT}; font-size: 14px;")

        v = QVBoxLayout(self); v.setContentsMargins(24,24,24,24); v.setSpacing(16)
        
        # Status Dropdown
        stat_row = QHBoxLayout()
        stat_row.addWidget(QLabel("Status:"))
        self.status_cb = QComboBox()
        self.status_cb.addItems(["Pending", "In Review", "Resolved", "Rejected"])
        self.status_cb.setCurrentText(current_status)
        self.status_cb.setStyleSheet(f"background: {PANEL_HI}; border: 1px solid {BORDER}; border-radius: 4px; padding: 4px;")
        stat_row.addWidget(self.status_cb); stat_row.addStretch(1)
        v.addLayout(stat_row)

        v.addWidget(QLabel("Question:"))
        q_lbl = QLabel(q_text)
        q_lbl.setWordWrap(True)
        q_lbl.setStyleSheet(f"background: {PANEL_HI}; border: 1px solid {BORDER}; border-radius: 8px; padding: 10px; color: {ACCENT_HI};")
        v.addWidget(q_lbl)

        v.addWidget(QLabel("Draft Answer (Verified Knowledge Base):"))
        self.a_input = QTextEdit()
        self.a_input.setPlaceholderText("Type the verified answer here...")
        self.a_input.setStyleSheet(f"background: {PANEL_HI}; border: 1px solid {BORDER}; border-radius: 8px; padding: 10px;")
        v.addWidget(self.a_input)

        acts = QHBoxLayout()
        acts.addStretch(1)
        save_status = QPushButton("Save Status Only"); save_status.clicked.connect(self._save_status)
        save_status.setStyleSheet(f"padding: 8px 16px; border-radius: 8px; background: {PANEL_HI}; border: 1px solid {BORDER};")
        
        publish = QPushButton("Publish to Knowledge Base"); publish.clicked.connect(self._publish)
        publish.setStyleSheet(f"padding: 8px 16px; border-radius: 8px; background: {SUCCESS}; color: white; font-weight: bold;")
        acts.addWidget(save_status); acts.addWidget(publish)
        v.addLayout(acts)

        self.action_taken = None

    def _save_status(self):
        self.action_taken = ("STATUS", self.status_cb.currentText())
        self.accept()

    def _publish(self):
        ans = self.a_input.toPlainText().strip()
        if not ans:
            QMessageBox.warning(self, "Error", "Answer cannot be empty to publish.")
            return
        self.action_taken = ("PUBLISH", self.status_cb.currentText(), ans)
        self.accept()


class UnansweredPage(QWidget):
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

        self.service = AdminService()
        self.v = QVBoxLayout(self); self.v.setContentsMargins(30,28,30,28); self.v.setSpacing(16)

        head = QLabel("Unanswered Questions")
        head.setStyleSheet(f"color:{TEXT}; font-size:26px; font-weight:800;")
        self.v.addWidget(head)
        sub = QLabel("Questions GramAI could not answer. Review and publish answers to the verified Knowledge Base.")
        sub.setStyleSheet(f"color:{TEXT_MUTED}; font-size:14px;")
        self.v.addWidget(sub)

        # Toolbar
        bar = QHBoxLayout(); bar.setSpacing(10)
        self.search = QLineEdit(); self.search.setPlaceholderText("🔍  Search questions…"); self.search.setMinimumHeight(42)
        bar.addWidget(self.search, 1)
        self.search.textChanged.connect(self._filter_rows)
        self.v.addLayout(bar)

        self.table = QTableWidget()
        self.v.addWidget(self.table, 1)
        self._load_data()

    def _load_data(self):
        self.queries_data = self.service.get_unanswered_queries()
        
        self.table.clear()
        self.table.setRowCount(len(self.queries_data))
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Question", "Freq", "First Asked", "Last Asked", "Status", "Actions"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(False)
        self.table.verticalHeader().setDefaultSectionSize(68)
        h = self.table.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for i in (1,2,3,4,5):
            h.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)

        self.table.setWordWrap(True)
        self.table.setTextElideMode(Qt.TextElideMode.ElideRight)
        for r, query in enumerate(self.queries_data):
            qid = query['id']
            q_text = str(query['raw_query_telugu'])
            freq = str(query['frequency'])
            first_asked = str(query.get('first_asked_date', ''))[:10]
            last_asked = str(query['last_asked']).split('.')[0]
            status = query.get('status', 'Pending') or 'Pending'
            
            self.table.setItem(r, 0, QTableWidgetItem("  " + q_text))
            self.table.setItem(r, 1, QTableWidgetItem(f"  {freq}"))
            self.table.setItem(r, 2, QTableWidgetItem("  " + first_asked))
            self.table.setItem(r, 3, QTableWidgetItem("  " + last_asked))

            color = WARNING if status == "Pending" else (SUCCESS if status in ["In Review", "Resolved"] else "#EF4444")
            if status == "Resolved": color = "#10B981"
            chip = QLabel(status)
            chip.setStyleSheet(
                f"color:{color}; background: rgba(255,255,255,15); "
                f"border-radius:10px; padding:4px 10px; font-size:12px; font-weight:700;"
            )
            chip_wrap = QWidget(); cw = QHBoxLayout(chip_wrap); cw.setContentsMargins(8,0,8,0); cw.addWidget(chip); cw.addStretch(1)
            self.table.setCellWidget(r, 4, chip_wrap)

            btn = QPushButton("Review"); btn.setObjectName("Primary")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, qid=qid, txt=q_text, st=status: self._review_query(qid, txt, st))
            btn_wrap = QWidget(); bw = QHBoxLayout(btn_wrap); bw.setContentsMargins(8,6,8,6); bw.addWidget(btn)
            self.table.setCellWidget(r, 5, btn_wrap)

    def _review_query(self, query_id, q_text, status):
        dlg = ReviewDialog(self, query_id, q_text, status)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            if dlg.action_taken[0] == "STATUS":
                self.service.update_unanswered_query_status(query_id, dlg.action_taken[1])
            elif dlg.action_taken[0] == "PUBLISH":
                ans = dlg.action_taken[2]
                self.service.publish_cached_response(q_text, ans)
                self.service.update_unanswered_query_status(query_id, "Resolved")
            self._load_data()

    def _filter_rows(self, text):
        term = text.strip().casefold()
        for row, query in enumerate(self.queries_data):
            self.table.setRowHidden(row, term not in str(query.get("raw_query_telugu", "")).casefold())
