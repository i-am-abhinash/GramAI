"""Shared admin glass controls. Qt gradients simulate glass without native blur."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout, QDialog, QVBoxLayout, QFrame, QScrollArea, QSizePolicy

SURFACE = "qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 rgba(24,65,105,218),stop:0.48 rgba(9,23,48,220),stop:1 rgba(43,25,76,210))"
ROW = "qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 rgba(24,53,91,205),stop:1 rgba(16,23,52,220))"
EDGE = "qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #69C9F8,stop:0.55 #42649D,stop:1 #8668C7)"
ADMIN_QSS = """
QWidget#AdminContentPage, QWidget#AdminContentPage QWidget#GlassCell { background: transparent; }
QWidget#AdminContentPage QLabel { background: transparent; border: none; }
QTableWidget {
    background: """ + SURFACE + """;
    border: 1px solid """ + EDGE + """;
    border-radius: 18px; gridline-color: transparent;
    color: #F3F7FF; selection-background-color: #233D6B;
    alternate-background-color: rgba(37,61,102,100);
    font-size: 14px;
}
QTableWidget QHeaderView, QTableWidget QWidget#qt_scrollarea_viewport { background: transparent; }
QHeaderView::section {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #24456D,stop:1 #14264B);
    color: #9DCDFF; border: none; border-bottom: 1px solid #4B70A4;
    font-size: 13px; font-weight: 700; padding: 10px 6px;
}
QTableWidget::item { background: rgba(12,28,54,125); padding: 6px 8px; border-bottom: 1px solid rgba(98,141,204,65); }
QTableWidget::item:selected { background: rgba(51,94,156,150); color: white; }
QLineEdit, QTextEdit, QPlainTextEdit, QComboBox {
    background: """ + ROW + """; border: 1px solid """ + EDGE + """;
    border-radius: 12px; padding: 8px 12px; color: #F3F7FF; font-size: 14px;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus { border: 1px solid #86D8FF; }
QComboBox { padding-right: 32px; min-height: 22px; }
QComboBox::drop-down { background: transparent; border: none; width: 28px; subcontrol-origin: padding; subcontrol-position: top right; }
QComboBox QAbstractItemView { background: #132745; border: 1px solid #588BC1; color: white; selection-background-color: #294D80; padding: 4px; }
QPushButton, QPushButton#Primary, QPushButton#Ghost {
    background: """ + SURFACE + """; border: 1px solid """ + EDGE + """;
    border-radius: 13px; padding: 8px 15px; color: #F4F8FF; font-weight: 600; font-size: 14px;
}
QPushButton:hover, QPushButton#Primary:hover, QPushButton#Ghost:hover { background: #294B80; border: 1px solid #9EDAFF; color: white; }
QPushButton:pressed { background: #142B50; }
QPushButton:disabled { background: #17243B; color: #8192AE; border-color: #354563; }
QDialog, QMessageBox, QInputDialog { background: #101E39; }
QDialog QLabel, QMessageBox QLabel { background: transparent; color: #F3F7FF; }
QScrollBar:vertical { background: transparent; width: 9px; margin: 3px; }
QScrollBar:horizontal { background: transparent; height: 9px; margin: 3px; }
QScrollBar::handle:vertical, QScrollBar::handle:horizontal { background: #46699A; border-radius: 4px; min-height: 25px; min-width: 25px; }
QScrollBar::add-line, QScrollBar::sub-line { width: 0; height: 0; }
"""
TONES = {
    "blue": ("#A9D7FF", "#4C92D6", "rgba(27,76,135,205)", "rgba(43,30,87,210)"),
    "green": ("#65F0CE", "#35A88E", "rgba(16,84,84,210)", "rgba(17,42,65,220)"),
    "amber": ("#FFD17A", "#B68A45", "rgba(94,66,28,210)", "rgba(42,36,49,220)"),
    "red": ("#FF9AAB", "#C45E77", "rgba(104,39,58,210)", "rgba(52,26,62,220)"),
}
def tint_style(tone="blue", button=False):
    fg, edge, start, end = TONES[tone]
    kind = "QPushButton" if button else "QLabel"
    css = f"{kind} {{ color: {fg}; background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 {start},stop:1 {end}); border:1px solid {edge}; border-radius:11px; padding:5px 9px; font-size:13px; font-weight:600; }}"
    if button:
        css += f" QPushButton:hover {{ border: 1px solid {fg}; color: white; background: {start}; }} QPushButton:pressed {{ background: {end}; }}"
    return css

def glass_button(text, tone="blue"):
    b = QPushButton(text)
    b.setStyleSheet(tint_style(tone, True))
    b.setMinimumHeight(36)
    b.setMinimumWidth(b.sizeHint().width() + 8)
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    return b

def badge(text, tone="blue"):
    b = QLabel(str(text))
    b.setAlignment(Qt.AlignmentFlag.AlignCenter)
    b.setStyleSheet(tint_style(tone))
    b.setMinimumHeight(32)
    b.setMinimumWidth(b.sizeHint().width() + 8)
    return b

def cell(*widgets):
    w = QWidget()
    w.setObjectName("GlassCell")
    w.setStyleSheet("QWidget#GlassCell { background: transparent; border: none; }")
    h = QHBoxLayout(w)
    h.setContentsMargins(5,4,5,4)
    h.setSpacing(5)
    for item in widgets:
        h.addWidget(item, 0, Qt.AlignmentFlag.AlignVCenter)
    h.addStretch()
    return w

def set_cell(table, row, col, *widgets):
    w = cell(*widgets)
    table.setCellWidget(row, col, w)
    table.setColumnWidth(col, max(table.columnWidth(col), w.sizeHint().width()+8))

class GlassDialog(QDialog):
    """Frameless modal with a rounded glass panel, preserving normal accept/reject semantics."""
    def __init__(self, parent, title, subtitle="", width=620):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet(ADMIN_QSS + "QDialog#GlassModal { background: transparent; }")
        self.setObjectName("GlassModal")
        root = QVBoxLayout(self)
        root.setContentsMargins(12,12,12,12)
        panel = QFrame()
        panel.setObjectName("ModalPanel")
        panel.setStyleSheet("QFrame#ModalPanel { background: " + SURFACE + "; border: 1px solid " + EDGE + "; border-radius: 24px; }")
        root.addWidget(panel)
        self.body = QVBoxLayout(panel)
        self.body.setContentsMargins(24,22,24,22)
        self.body.setSpacing(14)
        head = QHBoxLayout()
        label = QLabel(title)
        label.setWordWrap(True)
        label.setStyleSheet("background: transparent; font-size: 23px; font-weight: 700; color: #F4F8FF;")
        head.addWidget(label,1)
        close = glass_button("×")
        close.setFixedSize(40,36)
        close.clicked.connect(self.reject)
        head.addWidget(close)
        self.body.addLayout(head)
        if subtitle:
            hint = QLabel(subtitle)
            hint.setWordWrap(True)
            hint.setStyleSheet("background: transparent; color: #C4D6F0; font-size: 14px;")
            self.body.addWidget(hint)
        self.resize(width, 380)
        self._overlay = None

    def exec(self):
        parent = self.parentWidget()
        if parent is not None:
            host = parent.window()
            self._overlay = QWidget(host)
            self._overlay.setStyleSheet("background: rgba(2,6,18,155);")
            self._overlay.setGeometry(host.rect())
            self._overlay.show()
            self._overlay.raise_()
        try:
            return super().exec()
        finally:
            if self._overlay is not None:
                self._overlay.hide()
                self._overlay.deleteLater()
                self._overlay = None

def confirm(parent, title, message, action="Confirm", tone="blue"):
    dialog = GlassDialog(parent, title, message, 520)
    row = QHBoxLayout()
    row.addStretch()
    cancel = glass_button("Cancel")
    cancel.clicked.connect(dialog.reject)
    row.addWidget(cancel)
    yes = glass_button(action, tone)
    yes.clicked.connect(dialog.accept)
    row.addWidget(yes)
    dialog.body.addLayout(row)
    dialog.resize(520,220)
    return dialog.exec() == QDialog.DialogCode.Accepted
