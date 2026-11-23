"""FAQ Management page."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QAbstractItemView, QFrame, QDialog, QTextEdit, QMessageBox)
from theme import PANEL, PANEL_HI, ACCENT_HI, BORDER, TEXT, TEXT_MUTED
from backend.services.admin_service import AdminService

class FaqDialog(QDialog):
    def __init__(self, parent=None, faq_id=None, q_text="", a_text=""):
        super().__init__(parent)
        self.faq_id = faq_id
        self.setWindowTitle("Edit FAQ" if faq_id else "Add FAQ")
        self.setFixedSize(500, 400)
        self.setStyleSheet(f"background: {PANEL}; color: {TEXT}; font-size: 14px;")

        v = QVBoxLayout(self); v.setContentsMargins(24,24,24,24); v.setSpacing(16)
        
        v.addWidget(QLabel("Question:"))
        self.q_input = QLineEdit(q_text)
        self.q_input.setStyleSheet(f"background: rgba(31,58,96,0.92); border: 1px solid #43658B; border-radius: 20px; padding: 10px;")
        v.addWidget(self.q_input)

        v.addWidget(QLabel("Answer:"))
        self.a_input = QTextEdit(a_text)
        self.a_input.setStyleSheet(f"background: rgba(31,58,96,0.92); border: 1px solid #43658B; border-radius: 20px; padding: 10px;")
        v.addWidget(self.a_input)

        acts = QHBoxLayout()
        acts.addStretch(1)
        cancel = QPushButton("Cancel"); cancel.clicked.connect(self.reject)
        cancel.setStyleSheet(f"padding: 8px 16px; border-radius: 20px; background: rgba(31,58,96,0.92); border: 1px solid #43658B;")
        save = QPushButton("Save"); save.clicked.connect(self.accept)
        save.setStyleSheet(f"padding: 8px 16px; border-radius: 20px; background: {ACCENT_HI}; color: white; font-weight: bold;")
        acts.addWidget(cancel); acts.addWidget(save)
        v.addLayout(acts)

    def get_data(self):
        return self.q_input.text().strip(), self.a_input.toPlainText().strip()


class FaqPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.service = AdminService()
        self.v = QVBoxLayout(self); self.v.setContentsMargins(30,28,30,28); self.v.setSpacing(16)

        head_row = QHBoxLayout()
        head = QLabel("FAQ Management")
        head.setStyleSheet(f"color:{TEXT}; font-size:26px; font-weight:800;")
        head_row.addWidget(head); head_row.addStretch(1)
        
        add = QPushButton("+ Add FAQ"); add.setObjectName("Primary"); add.setMinimumHeight(42)
        add.clicked.connect(self._add_faq)
        head_row.addWidget(add)
        self.v.addLayout(head_row)

        sub = QLabel("Manage frequently asked questions to instantly resolve citizen queries.")
        sub.setStyleSheet(f"color:{TEXT_MUTED}; font-size:14px;")
        self.v.addWidget(sub)

        # Toolbar
        bar = QHBoxLayout(); bar.setSpacing(10)
        search = QLineEdit(); search.setPlaceholderText("🔍  Search FAQs…"); search.setMinimumHeight(42)
        bar.addWidget(search, 1)
        self.v.addLayout(bar)

        self.table = QTableWidget()
        self.v.addWidget(self.table, 1)
        self._load_data()

    def _load_data(self):
        self.faq_data = self.service.get_all_faqs()
        
        self.table.clear()
        self.table.setRowCount(len(self.faq_data))
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Question", "Answer", "Frequency", "Actions"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setDefaultSectionSize(64)
        h = self.table.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        h.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        h.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        h.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        for r, faq in enumerate(self.faq_data):
            faq_id = faq['id']
            q_text = str(faq['question'])
            a_text = str(faq['answer'])
            
            disp_a = a_text if len(a_text) <= 80 else a_text[:77] + "..."
            freq = str(faq['frequency'])
            
            self.table.setItem(r, 0, QTableWidgetItem("  " + q_text))
            self.table.setItem(r, 1, QTableWidgetItem("  " + disp_a))
            self.table.setItem(r, 2, QTableWidgetItem(f"  {freq} asks"))

            actions = QHBoxLayout(); actions.setContentsMargins(8,6,8,6); actions.setSpacing(4)
            e = QPushButton("✏️"); e.setObjectName("Ghost"); e.setFixedSize(32,32)
            e.clicked.connect(lambda _, fid=faq_id, q=q_text, a=a_text: self._edit_faq(fid, q, a))
            dl = QPushButton("🗑"); dl.setObjectName("Ghost"); dl.setFixedSize(32,32)
            dl.clicked.connect(lambda _, fid=faq_id: self._delete_faq(fid))
            
            actions.addWidget(e); actions.addWidget(dl)
            w = QWidget(); w.setLayout(actions)
            self.table.setCellWidget(r, 3, w)

    def _add_faq(self):
        dlg = FaqDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            q, a = dlg.get_data()
            if q and a:
                self.service.add_faq(q, a)
                self._load_data()

    def _edit_faq(self, faq_id, q_text, a_text):
        dlg = FaqDialog(self, faq_id, q_text, a_text)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            q, a = dlg.get_data()
            if q and a:
                self.service.update_faq(faq_id, q, a)
                self._load_data()

    def _delete_faq(self, faq_id):
        reply = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this FAQ?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.service.delete_faq(faq_id)
            self._load_data()
