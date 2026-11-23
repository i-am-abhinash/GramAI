"""Consistent glass-styled information dialogs for GramAI."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QListWidget
from widgets.aurora import AuroraSurface
from widgets.components import GlassButton

class GlassDialog(QDialog):
    def __init__(self,title,message="",parent=None):
        super().__init__(parent)
        self.setWindowTitle(title);self.setMinimumWidth(450)
        self.setStyleSheet("QDialog {background:#030B1D;} QLabel {color:#EAF5FF; background:transparent;} QListWidget {background:#0A1A32; color:white; border:1px solid #376B99; border-radius:15px; padding:8px;} QListWidget::item {padding:12px; border-bottom:1px solid #1C4568;} QListWidget::item:selected {background:#235784;}")
        outer=QVBoxLayout(self);outer.setContentsMargins(0,0,0,0)
        surface=AuroraSurface();outer.addWidget(surface)
        self.content=QVBoxLayout(surface);self.content.setContentsMargins(24,22,24,22);self.content.setSpacing(16)
        heading=QLabel("ⓘ  "+title);heading.setStyleSheet("font-size:20px; font-weight:700; color:#EAF7FF;")
        self.content.addWidget(heading)
        if message:
            body=QLabel(message);body.setWordWrap(True)
            body.setStyleSheet("font-size:15px; color:#D6E9FA;")
            self.content.addWidget(body)
        self.actions=QHBoxLayout();self.actions.addStretch()
        self.content.addLayout(self.actions)
    def add_button(self,text="✓  OK",callback=None):
        button=GlassButton(text,pill=True);button.setMinimumWidth(120)
        button.clicked.connect(callback or self.accept)
        self.actions.addWidget(button)
        return button

def show_message(parent,title,message):
    dialog=GlassDialog(title,message,parent);dialog.add_button();dialog.exec()
