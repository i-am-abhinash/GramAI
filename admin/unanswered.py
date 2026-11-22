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
        self.service = AdminService()
        self.queries_data = []
        self.filtered_data = []
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
        self.queries_data = self.service.get_unanswered_queries()
        self._apply_filter()

    def _apply_filter(self):
        query = self.search.text().lower().strip()
        if not query:
            self.filtered_data = self.queries_data
        else:
            self.filtered_data = [
                q for q in self.queries_data 
                if query in str(q.get('query_text', '')).lower() or query in str(q.get('status', '')).lower()
            ]
        self._render_table(self.filtered_data)

    def _render_table(self, data):
        self.table.clear()
        self.table.setRowCount(len(data))
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Unanswered Query", "Frequency", "First Asked", "Last Asked", "Status", "Action"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setDefaultSectionSize(54)
        
        h = self.table.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        h.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        h.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        h.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        h.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        h.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        h.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)

        for r, query in enumerate(data):
            qid = str(query['id'])
            q_text = str(query['query_text'])
            freq = str(query['frequency'])
            first_asked = str(query.get('first_asked_date', ''))[:10]
            last_asked = str(query['last_asked']).split('.')[0]
            status = query.get('status', 'Pending') or 'Pending'
            
            self.table.setItem(r, 0, QTableWidgetItem("  " + qid))
            self.table.setItem(r, 1, QTableWidgetItem("  " + q_text))
            self.table.setItem(r, 2, QTableWidgetItem(f"  {freq}"))
            self.table.setItem(r, 3, QTableWidgetItem("  " + first_asked))
            self.table.setItem(r, 4, QTableWidgetItem("  " + last_asked))

            color = WARNING if status == "Pending" else (SUCCESS if status in ["In Review", "Resolved"] else "#EF4444")
            if status == "Resolved": color = "#10B981"
            chip = QLabel(status)
            chip.setStyleSheet(
                f"color:{color}; background: rgba(255,255,255,15); "
                f"border-radius:10px; padding:4px 10px; font-size:12px; font-weight:700;"
            )
            chip_wrap = QWidget(); cw = QHBoxLayout(chip_wrap); cw.setContentsMargins(8,0,8,0); cw.addWidget(chip); cw.addStretch(1)
            self.table.setCellWidget(r, 5, chip_wrap)

            btn = QPushButton("Review"); btn.setObjectName("Primary")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, qid=qid, txt=q_text, st=status: self._review_query(qid, txt, st))
            btn_wrap = QWidget(); bw = QHBoxLayout(btn_wrap); bw.setContentsMargins(8,6,8,6); bw.addWidget(btn)
            self.table.setCellWidget(r, 6, btn_wrap)

    def _show_toast(self, msg, level="success"):
        if hasattr(self.window(), "show_toast"):
            self.window().show_toast(msg, level)

    def _review_query(self, query_id, q_text, status):
        dlg = ReviewDialog(self, query_id, q_text, status)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            if dlg.action_taken[0] == "STATUS":
                self.service.update_unanswered_query_status(query_id, dlg.action_taken[1])
                self._show_toast(f"Status updated to {dlg.action_taken[1]}", "success")
            elif dlg.action_taken[0] == "PUBLISH":
                ans = dlg.action_taken[2]
                self.service.publish_cached_response(q_text, ans)
                self.service.update_unanswered_query_status(query_id, "Resolved")
                self._show_toast("Answer published to Knowledge Base!", "success")
            self.refresh_data()
