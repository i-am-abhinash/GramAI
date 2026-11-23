"""Unanswered Queries management page."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
                             QTableWidgetItem, QHeaderView, QAbstractItemView, QLineEdit,
                             QPushButton, QDialog, QTextEdit, QComboBox, QMessageBox)
from theme import TEXT, TEXT_MUTED, ACCENT, ACCENT_HI, SUCCESS, WARNING
from backend.services.admin_service import AdminService

class ReviewDialog(QDialog):
    def __init__(self, parent, query_id, query_text, current_status):
        super().__init__(parent)
        self.setWindowTitle(f"Review Query #{query_id}")
        self.resize(500, 360)
        self.query_id = query_id
        self.action_taken = None
        
        v = QVBoxLayout(self); v.setSpacing(14)
        
        q_lbl = QLabel(f"<b>Query:</b> {query_text}")
        q_lbl.setWordWrap(True)
        v.addWidget(q_lbl)
        
        # Status change row
        h1 = QHBoxLayout()
        h1.addWidget(QLabel("Update Status:"))
        self.status_cb = QComboBox()
        self.status_cb.addItems(["Pending", "In Review", "Resolved", "Ignored"])
        self.status_cb.setCurrentText(current_status)
        h1.addWidget(self.status_cb)
        btn_status = QPushButton("Save Status")
        btn_status.clicked.connect(self._save_status)
        h1.addWidget(btn_status)
        v.addLayout(h1)
        
        v.addWidget(QLabel("<b>Provide Official Answer (Publishes to Cache):</b>"))
        self.ans_edit = QTextEdit()
        self.ans_edit.setPlaceholderText("Type Telugu/English response to cache for this question...")
        v.addWidget(self.ans_edit)
        
        btn_publish = QPushButton("Publish Answer & Resolve")
        btn_publish.setObjectName("Primary")
        btn_publish.clicked.connect(self._publish_answer)
        v.addWidget(btn_publish)
        
    def _save_status(self):
        new_status = self.status_cb.currentText()
        self.action_taken = ("STATUS", new_status)
        self.accept()
        
    def _publish_answer(self):
        ans = self.ans_edit.toPlainText().strip()
        if not ans:
            QMessageBox.warning(self, "Empty Answer", "Please enter an answer before publishing.")
            return
        self.action_taken = ("PUBLISH", "Resolved", ans)
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
        self.queries_data = []
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
        self.refresh_data()

    def refresh_data(self):
        self.queries_data = self.service.get_unanswered_queries()
        self._render_table(self.queries_data)
        self._filter_rows(self.search.text())

    def _render_table(self, data):
        self.table.clear()
        self.table.setRowCount(len(data))
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Unanswered Query", "Frequency", "First Asked", "Last Asked", "Status", "Action"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(False)
        self.table.verticalHeader().setDefaultSectionSize(68)
        self.table.setWordWrap(True)
        self.table.setTextElideMode(Qt.TextElideMode.ElideRight)

        h = self.table.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        h.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        h.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        h.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        h.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        h.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        h.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)

        for r, query in enumerate(data):
            qid = str(query.get('id', ''))
            q_text = str(query.get('query_text') or query.get('raw_query_telugu', ''))
            freq = str(query.get('frequency', 1))
            first_asked = str(query.get('first_asked_date', ''))[:10]
            last_asked = str(query.get('last_asked', '')).split('.')[0]
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

    def _filter_rows(self, text):
        term = text.strip().casefold()
        for row, query in enumerate(self.queries_data):
            q_text = str(query.get('query_text') or query.get('raw_query_telugu', '')).casefold()
            self.table.setRowHidden(row, term not in q_text)
