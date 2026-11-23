"""Reusable dark-glass dialog with content above a fixed bottom action row."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QFrame
from widgets.aurora import AuroraSurface
from widgets.components import GlassButton

class GlassDialog(QDialog):
    def __init__(self,title,message="",parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(680,510)
        self.setMinimumSize(480,360)
        self.setStyleSheet("""
            QDialog { background:#03091B; }
            QLabel { background:transparent; color:#EAF5FF; }
            QListWidget {background:rgba(9,25,48,0.88);color:#EAF5FF;
                border:1px solid #4085B1;border-radius:18px;padding:7px;}
            QListWidget::item {padding:16px 14px;border-bottom:1px solid #244E76;}
            QListWidget::item:selected {background:#224B80;color:white;}
            QScrollBar:vertical {background:#09172A;width:8px;}
            QScrollBar::handle:vertical {background:#3977A4;border-radius:4px;}
        """)
        outer=QVBoxLayout(self);outer.setContentsMargins(0,0,0,0)
        surface=AuroraSurface();outer.addWidget(surface)
        body=QVBoxLayout(surface);body.setContentsMargins(26,22,26,24);body.setSpacing(14)
        heading=QLabel("ⓘ  "+title)
        heading.setStyleSheet("background:transparent;color:#EAF7FF;font-size:23px;font-weight:700;")
        body.addWidget(heading)
        self.content=QVBoxLayout()
        self.content.setSpacing(12)
        body.addLayout(self.content,1)
        if message:
            label=QLabel(message);label.setWordWrap(True)
            label.setStyleSheet("background:transparent;color:#D6E9FA;font-size:16px;")
            self.content.addWidget(label)
        self.actions=QHBoxLayout();self.actions.setSpacing(10);self.actions.addStretch(1)
        body.addLayout(self.actions)
    def add_button(self,text="✓  OK",callback=None):
        button=GlassButton(text,pill=True)
        button.setMinimumSize(132,46)
        button.clicked.connect(callback or self.accept)
        self.actions.addWidget(button)
        return button

def show_message(parent,title,message):
    dialog=GlassDialog(title,message,parent)
    dialog.add_button()
    dialog.exec()
